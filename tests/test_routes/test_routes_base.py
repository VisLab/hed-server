import io
import os

from tests.test_web_base import TestWebBase

# from tests.test_routes.test_routes_base import TestRouteBase

class TestRouteBase(TestWebBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def _get_path(self, filename):
        filename_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/")
        return os.path.join(filename_path, filename)

    def _get_file_buffer(self, filename, name=None):
        filename = self._get_path(filename)
        with open(filename, 'rb') as f:
            x = f.read()
        input_buffer = io.BytesIO(bytes(x))

        if not name:
            name = os.path.split(filename)[1]

        return input_buffer, name

    def _get_file_string(self, filename):
        filename = self._get_path(filename)
        with open(filename, 'rb') as fp:
            filename_string = fp.read().decode('utf-8')

        return filename_string
