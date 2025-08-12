"""
This module contains the factory for creating the HEDTools application.
"""

from flask import Flask
from flask_wtf.csrf import CSRFProtect
import importlib
from config import Config


class AppFactory:
    """A factory for creating the HEDTools application.

    This factory is used to create a Flask application with the given configuration.
    It also sets up CSRF protection for the application.
    """

    @staticmethod
    def create_app(config_class) -> Flask:
        """Creates the Flask app and registers the blueprints.

        Args:
            config_class (class): A class containing the configuration variables.

        Returns:
            Flask: The initialized Flask app.
        """
        static_url_path = AppFactory.get_static_url_path(config_class)
        app = Flask(__name__, static_url_path=static_url_path)
        app.config.from_object(config_class)
        CSRFProtect(app)
        return app

    @staticmethod
    def get_static_url_path(config_class) -> str:
        """Gets the static URL path from the config class.

        Args:
            config_class (class): A class containing the configuration variables.

        Returns:
            str: The static URL path.
        """
        config_module_name, config_class_name = config_class.split(".")
        config_module = importlib.import_module(config_module_name)
        config_class = getattr(config_module, config_class_name)
        return getattr(config_class, Config.STATIC_URL_PATH_ATTRIBUTE_NAME, None)
