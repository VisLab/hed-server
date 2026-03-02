"""
This module contains the configurations for the HEDTools application.
"""

import os
import tempfile


def _read_or_create_secret_key(path: str) -> str:
    """Read SECRET_KEY from *path*, creating the file if it doesn't exist.

    Falls back to a random key if the directory is not accessible (e.g. during
    test runs or CI where /var/log/hedtools/ has not been created yet).
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(str(os.urandom(24)))
        with open(path) as f:
            return f.read()
    except OSError:
        return str(os.urandom(24))


class Config:
    LOG_DIRECTORY = "/var/log/hedtools"
    LOG_FILE = os.path.join(LOG_DIRECTORY, "error.log")
    SECRET_KEY = os.getenv("SECRET_KEY") or _read_or_create_secret_key("/var/log/hedtools/tmp.txt")
    STATIC_URL_PATH = None
    STATIC_URL_PATH_ATTRIBUTE_NAME = "STATIC_URL_PATH"
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "hedtools_uploads")
    URL_PREFIX = None
    HED_CACHE_FOLDER = "/var/cache/schema_cache"


class DevelopmentConfig(Config):
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Default to production values, can be overridden by environment variables
    URL_PREFIX = os.getenv("HED_URL_PREFIX", "/hed")
    STATIC_URL_PATH = os.getenv("HED_STATIC_URL_PATH", "/hed/hedweb/static")


class ProductionDevConfig(Config):
    DEBUG = False
    TESTING = False
    URL_PREFIX = "/hed_dev"
    STATIC_URL_PATH = "/hed_dev/hedweb/static"


class TestConfig(Config):
    DEBUG = False
    TESTING = True


class DebugConfig(Config):
    DEBUG = True
    TESTING = False
