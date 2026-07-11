import importlib.util
import os

# Force a TestConfig-based config *before* any test module gets a chance to import
# hedweb.runserver. runserver.py builds a module-level `app = create_app_with_routes()` as a
# side effect of being imported (needed so Gunicorn can import hedtools.hedweb.runserver:app),
# and that app defaults to DevelopmentConfig (TESTING=False) unless HEDTOOLS_CONFIG_CLASS is
# already set - which meant, depending on which test file happened to import it first and how
# the suite was invoked, the background schema-version cache warmer (see
# hedweb.schema_version_warmer, started from AppFactory.create_app() whenever TESTING is not
# set) could end up actually running during a test session, hitting GitHub for real.
#
# AppFactory.create_app() also guards against this via _running_under_unittest(), but that
# check only recognizes `python -m unittest ...` specifically; some IDEs and other unittest
# front-ends run test discovery under a different __main__, which that check does not catch.
# Setting TESTING here is a second, runner-independent layer: this module (tests/__init__.py)
# is imported before any test module regardless of which front-end is driving unittest, so by
# the time anything imports hedweb.runserver, HEDTOOLS_CONFIG_CLASS is already pointing at a
# TestConfig and app.config["TESTING"] is already True.
#
# Only sets a default - never overrides a value a CI workflow or developer already exported.
if "HEDTOOLS_CONFIG_CLASS" not in os.environ:
    if importlib.util.find_spec("config"):
        os.environ["HEDTOOLS_CONFIG_CLASS"] = "config.TestConfig"
    else:
        os.environ["HEDTOOLS_CONFIG_CLASS"] = "default_config.TestConfig"
