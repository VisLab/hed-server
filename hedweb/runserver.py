import os
import sys
from logging import ERROR
from logging.handlers import RotatingFileHandler

# Ensure the parent directory is in the Python path so we can import config modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from hed import _version as vr  # noqa: E402

from hedweb._version import get_versions  # noqa: E402
from hedweb.app_factory import AppFactory  # noqa: E402

CONFIG_ENVIRON_NAME = "HEDTOOLS_CONFIG_CLASS"


def get_version_dict():
    """Create a dictionary of versions and related metadata.

    Returns:
        dict: Keys are tool_ver, tool_commit, web_ver, web_date.

    """

    web_dict = get_versions()
    # New hedtools version uses __version__ attribute instead of get_versions()
    tools_version = getattr(vr, "__version__", "unknown")
    tools_commit = getattr(vr, "__commit_id__", "")
    return {
        "tool_ver": tools_version,
        "tool_commit": tools_commit,
        "web_ver": web_dict["version"],
        "web_date": web_dict["date"],
    }


def setup_logging():
    """Sets up the current_application logging. If the log directory does not exist then there will be no logging."""
    if os.path.exists(app.config["LOG_DIRECTORY"]):
        file_handler = RotatingFileHandler(
            app.config["LOG_FILE"], maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(ERROR)
        app.logger.addHandler(file_handler)


def configure_app():
    """Configures the current application. Checks to see if a environment variable exist and if it doesn't then it
    defaults to another configuration.

    """
    if CONFIG_ENVIRON_NAME in os.environ:
        config_class = os.environ.get(CONFIG_ENVIRON_NAME)
    else:
        # Try to use config.DevelopmentConfig, fallback to default_config if not available
        try:
            import config  # noqa: F401  # only to test availability

            config_class = "config.DevelopmentConfig"
        except ImportError:
            config_class = "default_config.DevelopmentConfig"

    return AppFactory.create_app(config_class)


def create_app_with_routes():
    """Create and configure the Flask app with routes registered."""
    app = configure_app()
    with app.app_context():
        from hedweb.routes import route_blueprint

        app.register_blueprint(route_blueprint, url_prefix=app.config["URL_PREFIX"])
    return app


# Create a module-level app so Gunicorn can import hedtools.hedweb.runserver:app
app = create_app_with_routes()


def main():
    """Main entry point for the application."""
    setup_logging()
    import argparse

    parser = argparse.ArgumentParser(description="Run the HED web server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run the server on")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)


# Only run the server if executed directly
if __name__ == "__main__":
    main()
