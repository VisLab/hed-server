import time
import unittest
from unittest.mock import patch

from hedweb import schema_version_warmer


class Test(unittest.TestCase):
    def setUp(self):
        # Belt-and-suspenders: if anything earlier in the suite left a real (unmocked)
        # warmer thread running - e.g. because some other test imported hedweb.runserver
        # before tests/__init__.py's TESTING default took effect - start_warmer() below
        # would otherwise be a silent no-op against that pre-existing thread (it's
        # idempotent by design), and this test would then be exercising a mock that never
        # actually gets called. Stopping any warmer before each test guarantees a clean
        # slate regardless of what ran before it.
        schema_version_warmer.stop_warmer()

    def tearDown(self):
        schema_version_warmer.stop_warmer()

    def test_start_warmer_calls_get_available_hed_versions_repeatedly(self):
        with patch.object(schema_version_warmer.hedschema, "get_available_hed_versions") as mock_get:
            mock_get.return_value = {}
            schema_version_warmer.start_warmer(interval=0.05)
            # Give the background thread a few cycles to run.
            time.sleep(0.3)
            schema_version_warmer.stop_warmer()

            self.assertGreaterEqual(mock_get.call_count, 2)
            _, kwargs = mock_get.call_args
            self.assertEqual(kwargs.get("library_name"), "all")
            self.assertTrue(kwargs.get("check_prerelease"))

    def test_start_warmer_is_idempotent(self):
        with patch.object(schema_version_warmer.hedschema, "get_available_hed_versions") as mock_get:
            mock_get.return_value = {}
            first_event = schema_version_warmer.start_warmer(interval=0.05)
            second_event = schema_version_warmer.start_warmer(interval=0.05)
            self.assertIs(first_event, second_event)
            schema_version_warmer.stop_warmer()

    def test_warmer_survives_exceptions(self):
        with patch.object(schema_version_warmer.hedschema, "get_available_hed_versions") as mock_get:
            mock_get.side_effect = RuntimeError("GitHub unreachable")
            schema_version_warmer.start_warmer(interval=0.05)
            time.sleep(0.3)
            schema_version_warmer.stop_warmer()

            self.assertGreaterEqual(mock_get.call_count, 2)

    def test_stop_warmer_without_start_is_a_noop(self):
        # Should not raise even if a warmer was never started in this process.
        schema_version_warmer.stop_warmer()


if __name__ == "__main__":
    unittest.main()
