"""
Default configuration for CI environments and when config.py is not available.
"""

import os
import tempfile


class Config:
    BASE_DIRECTORY = os.environ.get("HED_BASE_DIRECTORY", tempfile.gettempdir())
    LOG_DIRECTORY = os.path.join(BASE_DIRECTORY, "log")

    # Ensure directories exist before setting file paths
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIRECTORY, "schema_cache"), exist_ok=True)

    LOG_FILE = os.path.join(LOG_DIRECTORY, "error.log")

    # Generate a simple secret key for CI/testing
    SECRET_KEY = os.environ.get("SECRET_KEY", "ci-test-key-not-secure")

    STATIC_URL_PATH = None
    STATIC_URL_PATH_ATTRIBUTE_NAME = "STATIC_URL_PATH"
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "hedtools_uploads")
    URL_PREFIX = None
    HED_CACHE_FOLDER = os.path.join(BASE_DIRECTORY, "schema_cache")


class DevelopmentConfig(Config):
    DEBUG = False
    TESTING = False


class TestConfig(Config):
    DEBUG = False
    TESTING = True
    # Use temporary directories for testing logs to avoid permission issues
    _test_base = tempfile.gettempdir()
    LOG_DIRECTORY = os.path.join(_test_base, "hedtools_test_log")

    # For tests, try to use a persistent cache if available, otherwise use temp
    # This allows tests to work whether schemas are pre-cached or not
    _persistent_cache = os.path.join(Config.BASE_DIRECTORY, "schema_cache")
    if os.path.exists(_persistent_cache):
        HED_CACHE_FOLDER = _persistent_cache
    else:
        HED_CACHE_FOLDER = os.path.join(_test_base, "hedtools_test_cache")
        os.makedirs(HED_CACHE_FOLDER, exist_ok=True)

    # Ensure test log directory is created
    os.makedirs(LOG_DIRECTORY, exist_ok=True)


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class DebugConfig(Config):
    DEBUG = True
    TESTING = False
