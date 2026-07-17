import os
import unittest
from unittest.mock import patch

from hedweb.app_factory import AppFactory, _running_under_unittest
from hedweb.schema_version_warmer import DEFAULT_REFRESH_INTERVAL


class _BaseConfig:
    SECRET_KEY = "test-key"
    STATIC_URL_PATH = None


class NonTestingConfig(_BaseConfig):
    TESTING = False
    DEBUG = False
    # The warmer is bypassed by default now (manifest fast path upstream); it only starts when
    # explicitly enabled. These configs opt in so the "starts" guards can still be exercised.
    SCHEMA_VERSION_WARM_ENABLED = True


class NonTestingDebugConfig(_BaseConfig):
    TESTING = False
    DEBUG = True
    SCHEMA_VERSION_WARM_ENABLED = True


class TestingConfig(_BaseConfig):
    TESTING = True
    DEBUG = False
    SCHEMA_VERSION_WARM_ENABLED = True


class CustomIntervalConfig(_BaseConfig):
    TESTING = False
    DEBUG = False
    SCHEMA_VERSION_WARM_ENABLED = True
    SCHEMA_VERSION_WARM_INTERVAL = 10


class WarmDisabledByDefaultConfig(_BaseConfig):
    # No SCHEMA_VERSION_WARM_ENABLED key at all - the warmer must stay off.
    TESTING = False
    DEBUG = False


class WarmExplicitlyDisabledConfig(_BaseConfig):
    TESTING = False
    DEBUG = False
    SCHEMA_VERSION_WARM_ENABLED = False


class TestRunningUnderUnittest(unittest.TestCase):
    """Directly exercises the helper create_app() relies on to detect a test run.

    This is the one piece of the warmer's startup guard that isn't obvious from reading
    the code - it deliberately checks the *identity* of the __main__ module rather than
    "unittest" in sys.modules, because the latter is true even during a normal run (Flask/
    Werkzeug import unittest.mock internally). These tests pin down exactly which shapes of
    __main__ do and don't count, independent of however this test file itself happens to be
    invoked.
    """

    def test_true_when_main_is_unittest_entrypoint(self):
        fake_main = type("FakeMain", (), {"__file__": "/usr/lib/python3.10/unittest/__main__.py"})
        with patch.dict("sys.modules", {"__main__": fake_main}):
            self.assertTrue(_running_under_unittest())

    def test_true_on_windows_style_path(self):
        fake_main = type("FakeMain", (), {"__file__": r"C:\Python310\Lib\unittest\__main__.py"})
        with patch.dict("sys.modules", {"__main__": fake_main}):
            self.assertTrue(_running_under_unittest())

    def test_false_for_ordinary_script(self):
        fake_main = type("FakeMain", (), {"__file__": "/home/user/myscript.py"})
        with patch.dict("sys.modules", {"__main__": fake_main}):
            self.assertFalse(_running_under_unittest())

    def test_false_when_main_has_no_file_attribute(self):
        # e.g. an interactive interpreter, where __main__ has no __file__ at all.
        fake_main = type("FakeMain", (), {})
        with patch.dict("sys.modules", {"__main__": fake_main}):
            self.assertFalse(_running_under_unittest())


class TestWarmerStartupGuards(unittest.TestCase):
    """Exercises AppFactory.create_app()'s decision of whether to start the background
    schema-version cache warmer (see hedweb.schema_version_warmer).

    Every real test process here is itself running under unittest, so create_app()'s own
    _running_under_unittest() guard would always skip starting the warmer - that's the
    correct behavior, but it means these tests have to patch that guard out in order to
    exercise the *other* conditions (TESTING, debug/reloader) in isolation. start_warmer()
    itself is also patched so nothing here ever spins up a real thread or touches the
    network, regardless of which branch is under test.
    """

    def setUp(self):
        patcher = patch("hedweb.app_factory._running_under_unittest", return_value=False)
        self.mock_running_under_unittest = patcher.start()
        self.addCleanup(patcher.stop)

        patcher2 = patch("hedweb.schema_version_warmer.start_warmer")
        self.mock_start_warmer = patcher2.start()
        self.addCleanup(patcher2.stop)

    def test_starts_when_not_testing_and_not_debug(self):
        AppFactory.create_app(NonTestingConfig)
        self.mock_start_warmer.assert_called_once()

    def test_skipped_when_warm_disabled_by_default(self):
        # No SCHEMA_VERSION_WARM_ENABLED key -> warmer stays bypassed even outside testing.
        AppFactory.create_app(WarmDisabledByDefaultConfig)
        self.mock_start_warmer.assert_not_called()

    def test_skipped_when_warm_explicitly_disabled(self):
        AppFactory.create_app(WarmExplicitlyDisabledConfig)
        self.mock_start_warmer.assert_not_called()

    def test_skipped_when_testing(self):
        AppFactory.create_app(TestingConfig)
        self.mock_start_warmer.assert_not_called()

    def test_skipped_under_unittest_regardless_of_config(self):
        self.mock_running_under_unittest.return_value = True
        AppFactory.create_app(NonTestingConfig)
        self.mock_start_warmer.assert_not_called()

    def test_skipped_in_debug_reloader_watcher_process(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("WERKZEUG_RUN_MAIN", None)
            AppFactory.create_app(NonTestingDebugConfig)
        self.mock_start_warmer.assert_not_called()

    def test_starts_in_debug_reloader_child_process(self):
        with patch.dict(os.environ, {"WERKZEUG_RUN_MAIN": "true"}):
            AppFactory.create_app(NonTestingDebugConfig)
        self.mock_start_warmer.assert_called_once()

    def test_uses_configured_interval(self):
        AppFactory.create_app(CustomIntervalConfig)
        self.mock_start_warmer.assert_called_once_with(10)

    def test_uses_default_interval_when_not_configured(self):
        AppFactory.create_app(NonTestingConfig)
        self.mock_start_warmer.assert_called_once_with(DEFAULT_REFRESH_INTERVAL)


if __name__ == "__main__":
    unittest.main()
