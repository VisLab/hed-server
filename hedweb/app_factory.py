"""
This module contains the factory for creating the HEDTools application.
"""

from flask import Flask
from flask_wtf.csrf import CSRFProtect
import importlib


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
        CSRFProtect(app)
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
            if config_module_name == 'config':
                config_module = importlib.import_module('default_config')
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
