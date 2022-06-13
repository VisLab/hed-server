import os
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request, Response

from hedweb.runserver import get_version_dict


class Test(unittest.TestCase):

    def test_get_versions(self):
        ver_dict = get_version_dict()
        self.assertIsInstance(ver_dict, dict, "get_version_dict returns a dictionary")
        self.assertIn('tool_ver', ver_dict, "get_version_dict has a tool_ver key")
        self.assertIn('tool_date', ver_dict, "get_version_dict has a tool_date key")
        self.assertIn('web_ver', ver_dict, "get_version_dict has a web_ver key")
        self.assertIn('web_date', ver_dict, "get_version_dict has a t]web_date key")