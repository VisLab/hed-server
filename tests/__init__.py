import importlib.util
import os

# Force a TestConfig-based config *before* any test module gets a chance to import
# hedweb.runserver. runserver.py builds a module-level `app = create_app_with_routes()` as a
# side effect of being imported (needed so Gunicorn can import hedtools.hedweb.runserver:app),
# and that app defaults to DevelopmentConfig (TESTING=False) unless HEDTOOLS_CONFIG_CLASS is
# already set. Pinning TestConfig here ensures the whole suite runs under a CI-safe config
# (TESTING=True, workspace-local cache/log dirs) regardless of which test module happens to
# import runserver first or which front-end is driving unittest - this module (tests/__init__.py)
# is imported before any test module in every case.
#
# Only sets a default - never overrides a value a CI workflow or developer already exported.
if "HEDTOOLS_CONFIG_CLASS" not in os.environ:
    if importlib.util.find_spec("config"):
        os.environ["HEDTOOLS_CONFIG_CLASS"] = "config.TestConfig"
    else:
        os.environ["HEDTOOLS_CONFIG_CLASS"] = "default_config.TestConfig"
