"""
Default configuration for CI environments and when config.py is not available.
"""

import os
import tempfile


class Config(object):
    BASE_DIRECTORY = os.environ.get('HED_BASE_DIRECTORY', tempfile.gettempdir())
    LOG_DIRECTORY = os.path.join(BASE_DIRECTORY, 'log')

    # Ensure directories exist before setting file paths
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIRECTORY, 'schema_cache'), exist_ok=True)

    LOG_FILE = os.path.join(LOG_DIRECTORY, 'error.log')

    # Generate a simple secret key for CI/testing
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ci-test-key-not-secure')
    
    STATIC_URL_PATH = None
    STATIC_URL_PATH_ATTRIBUTE_NAME = 'STATIC_URL_PATH'
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'hedtools_uploads')
    URL_PREFIX = None
    HED_CACHE_FOLDER = os.path.join(BASE_DIRECTORY, 'schema_cache')


class DevelopmentConfig(Config):
    DEBUG = False
    TESTING = False


class TestConfig(Config):
    DEBUG = False
    TESTING = True
    # Use temporary directories for testing to avoid permission issues
    BASE_DIRECTORY = tempfile.gettempdir()
    LOG_DIRECTORY = os.path.join(BASE_DIRECTORY, 'hedtools_test_log')
    HED_CACHE_FOLDER = os.path.join(BASE_DIRECTORY, 'hedtools_test_cache')

    # Ensure test directories are created
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    os.makedirs(HED_CACHE_FOLDER, exist_ok=True)


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class DebugConfig(Config):
    DEBUG = True
    TESTING = False
