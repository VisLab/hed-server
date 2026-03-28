import logging
import os
import tempfile
import unittest
from logging.handlers import RotatingFileHandler

from hedweb.runserver import get_version_dict


class Test(unittest.TestCase):
    def test_get_versions(self):
        ver_dict = get_version_dict()
        self.assertIsInstance(ver_dict, dict, "get_version_dict returns a dictionary")
        self.assertIn("tool_ver", ver_dict, "get_version_dict has a tool_ver key")
        self.assertIn("tool_commit", ver_dict, "get_version_dict has a tool_commit key")
        self.assertIn("web_ver", ver_dict, "get_version_dict has a web_ver key")
        self.assertIn("web_date", ver_dict, "get_version_dict has a t]web_date key")

    def test_setup_logging_with_log_directory(self):
        from hedweb.runserver import app, setup_logging

        hedweb_logger = logging.getLogger("hedweb")
        saved_handlers = hedweb_logger.handlers[:]
        saved_app_handlers = app.logger.handlers[:]

        with tempfile.TemporaryDirectory() as tmpdir:
            original_log_dir = app.config["LOG_DIRECTORY"]
            original_log_file = app.config["LOG_FILE"]
            try:
                app.config["LOG_DIRECTORY"] = tmpdir
                app.config["LOG_FILE"] = os.path.join(tmpdir, "test.log")
                hedweb_logger.handlers.clear()
                setup_logging()
                rotating_handlers = [h for h in hedweb_logger.handlers if isinstance(h, RotatingFileHandler)]
                self.assertTrue(
                    len(rotating_handlers) > 0,
                    "setup_logging attaches a RotatingFileHandler when LOG_DIRECTORY exists",
                )
            finally:
                for h in hedweb_logger.handlers:
                    h.close()
                hedweb_logger.handlers[:] = saved_handlers
                app.logger.handlers[:] = saved_app_handlers
                app.config["LOG_DIRECTORY"] = original_log_dir
                app.config["LOG_FILE"] = original_log_file

    def test_setup_logging_without_log_directory(self):
        from hedweb.runserver import app, setup_logging

        hedweb_logger = logging.getLogger("hedweb")
        saved_handlers = hedweb_logger.handlers[:]
        original_log_dir = app.config["LOG_DIRECTORY"]

        try:
            app.config["LOG_DIRECTORY"] = "/nonexistent/path/that/does/not/exist"
            hedweb_logger.handlers.clear()
            setup_logging()
            stream_handlers = [h for h in hedweb_logger.handlers if type(h) is logging.StreamHandler]
            self.assertTrue(
                len(stream_handlers) > 0,
                "setup_logging attaches a StreamHandler when LOG_DIRECTORY does not exist",
            )
        finally:
            for h in hedweb_logger.handlers:
                h.close()
            hedweb_logger.handlers[:] = saved_handlers
            app.config["LOG_DIRECTORY"] = original_log_dir

    def test_setup_logging_idempotent(self):
        from hedweb.runserver import app, setup_logging

        hedweb_logger = logging.getLogger("hedweb")
        saved_handlers = hedweb_logger.handlers[:]
        saved_app_handlers = app.logger.handlers[:]

        with tempfile.TemporaryDirectory() as tmpdir:
            original_log_dir = app.config["LOG_DIRECTORY"]
            original_log_file = app.config["LOG_FILE"]
            try:
                app.config["LOG_DIRECTORY"] = tmpdir
                app.config["LOG_FILE"] = os.path.join(tmpdir, "test.log")
                hedweb_logger.handlers.clear()
                setup_logging()
                count_after_first = len(hedweb_logger.handlers)
                setup_logging()
                self.assertEqual(
                    count_after_first,
                    len(hedweb_logger.handlers),
                    "setup_logging does not add duplicate handlers when called twice",
                )
            finally:
                for h in hedweb_logger.handlers:
                    h.close()
                hedweb_logger.handlers[:] = saved_handlers
                app.logger.handlers[:] = saved_app_handlers
                app.config["LOG_DIRECTORY"] = original_log_dir
                app.config["LOG_FILE"] = original_log_file
