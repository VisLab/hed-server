"""
This module contains the factory for creating the HEDTools application.
"""

import importlib
import sys

from flask import Flask
from flask_wtf.csrf import CSRFProtect


def _running_under_unittest() -> bool:
    """Best-effort detection of ``python -m unittest`` (including under coverage.py).

    Checking ``"unittest" in sys.modules`` is not enough - Flask/Werkzeug and other
    dependencies import ``unittest.mock`` for their own purposes, which pulls in the
    ``unittest`` package during perfectly normal runs too. Instead, check whether the
    ``__main__`` module actually *is* unittest's own entry point, which is only true when
    something ran ``python -m unittest ...`` - directly, via ``discover``, or wrapped by
    ``coverage run -m unittest ...`` (coverage.py traces execution without changing
    ``__main__``, so this still works under the coverage-wrapped invocation CI uses).

    Returns:
        bool: True if the current process's ``__main__`` module is unittest's own.
    """
    main_module = sys.modules.get("__main__")
    main_file = (getattr(main_module, "__file__", "") or "").replace("\\", "/")
    return main_file.endswith("unittest/__main__.py")


class AppFactory:
    """A factory for creating the HEDTools application.

    This factory is used to create a Flask application with the given configuration.
    It also sets up CSRF protection for the application.
    """

    @staticmethod
    def create_app(config_class) -> Flask:
        """Creates the Flask app and registers the blueprints.

        Args:
            config_class (str or class): A string path to config class or the actual config class.

        Returns:
            Flask: The initialized Flask app.
        """
        # If config_class is a string, resolve it to the actual class
        if isinstance(config_class, str):
            config_class = AppFactory._resolve_config_class(config_class)

        static_url_path = AppFactory._get_static_url_path_from_class(config_class)
        app = Flask(__name__, static_url_path=static_url_path)
        app.config.from_object(config_class)

        # Ensure runtime directories exist for any paths that are explicitly
        # configured.  Using LOG_DIRECTORY and HED_CACHE_FOLDER directly avoids
        # inadvertently creating ./log or ./schema_cache when BASE_DIRECTORY is
        # absent or empty.  OSErrors (permission denied, drive not mounted, etc.)
        # are logged as warnings so a misconfigured path doesn't prevent startup.
        import os

        for dir_key in ("LOG_DIRECTORY", "HED_CACHE_FOLDER"):
            target = app.config.get(dir_key, "")
            if target:
                try:
                    os.makedirs(target, exist_ok=True)
                except OSError as exc:
                    app.logger.warning("Could not create directory %s=%r: %s", dir_key, target, exc)

        # Configure hedtools to use the specified cache directory
        if "HED_CACHE_FOLDER" in app.config:
            import hed.schema as hedschema

            if hasattr(hedschema, "set_cache_directory"):
                hedschema.set_cache_directory(app.config["HED_CACHE_FOLDER"])
            else:
                app.logger.warning(
                    "HED_CACHE_FOLDER configured but hedtools version does not support set_cache_directory()"
                )

        CSRFProtect(app)

        # Keep hedtools' own available-versions cache warm in the background so the
        # schema-version dropdown (hedweb.routes.schema_versions_results) never blocks a
        # request on a live GitHub check. This only ever calls
        # hed.schema.get_available_hed_versions() - the same call the route itself makes -
        # on a timer; see hedweb.schema_version_warmer for details.
        #
        # Guarded against three cases where we don't want a live background thread:
        #   - app.config["TESTING"] (TestConfig) - the normal case for test-created apps.
        #   - _running_under_unittest() - hedweb/runserver.py builds its module-level `app`
        #     under DevelopmentConfig (TESTING is False there) purely as a side effect of
        #     being imported, and test files import it directly (e.g. to get
        #     get_version_dict()) without ever building a TestConfig app of their own. This
        #     catches that case regardless of which config the app ends up with.
        #   - Flask's debug reloader re-importing this module in a parent "watcher" process
        #     before spawning the real one (WERKZEUG_RUN_MAIN check).
        if (
            not app.config.get("TESTING")
            and not _running_under_unittest()
            and (not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true")
        ):
            from hedweb.schema_version_warmer import DEFAULT_REFRESH_INTERVAL, start_warmer

            start_warmer(app.config.get("SCHEMA_VERSION_WARM_INTERVAL", DEFAULT_REFRESH_INTERVAL))

        return app

    @staticmethod
    def _resolve_config_class(config_class_string):
        """Resolve a config class string to the actual class object."""
        config_module_name, config_class_name = config_class_string.split(".")

        try:
            config_module = importlib.import_module(config_module_name)
            config_class_obj = getattr(config_module, config_class_name, None)

            # If the class doesn't exist in the module, treat it as if the module import failed
            if config_class_obj is None:
                raise AttributeError(f"module '{config_module_name}' has no attribute '{config_class_name}'")

        except (ImportError, AttributeError):
            # Fallback to default_config if main config is not available or doesn't have the class
            if config_module_name == "config":
                config_module = importlib.import_module("default_config")
                config_class_obj = getattr(config_module, config_class_name)
            else:
                raise

        return config_class_obj

    @staticmethod
    def _get_static_url_path_from_class(config_class_obj):
        """Get static URL path from the actual config class object."""
        # Get the STATIC_URL_PATH_ATTRIBUTE_NAME from the config class
        # Try to get it from the config module first, then fallback to default
        try:
            from config import Config

            static_url_path_attr = Config.STATIC_URL_PATH_ATTRIBUTE_NAME
        except (ImportError, AttributeError):
            from default_config import Config

            static_url_path_attr = Config.STATIC_URL_PATH_ATTRIBUTE_NAME

        return getattr(config_class_obj, static_url_path_attr, None)

    @staticmethod
    def get_static_url_path(config_class) -> str:
        """Gets the static URL path from the config class.

        Args:
            config_class (str): A string path to the config class.

        Returns:
            str: The static URL path.
        """
        # This method is kept for backward compatibility
        if isinstance(config_class, str):
            config_class_obj = AppFactory._resolve_config_class(config_class)
            return AppFactory._get_static_url_path_from_class(config_class_obj)
        else:
            return AppFactory._get_static_url_path_from_class(config_class)
