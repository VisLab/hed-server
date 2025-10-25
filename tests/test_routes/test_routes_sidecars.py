import unittest

from flask import Response

from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_sidecars_results_empty_data(self):
        response = self.app.test.post('/sidecars_submit')
        self.assertEqual(200, response.status_code, 'HED sidecar request succeeds even when no data')
        self.assertTrue(isinstance(response, Response),
                        'sidecars_submit to short should return a Response when no data')
        header_dict = dict(response.headers)
        self.assertEqual("error", header_dict["Category"], "The header msg_category when no sidecar is error ")
        self.assertFalse(response.data, "The response data for empty sidecar request is empty")

    def test_sidecars_results_to_long_valid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.0.0',
                          bc.COMMAND_OPTION: bc.COMMAND_TO_LONG,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/sidecars_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'sidecars_submit should return a Response when valid to long sidecar')
            self.assertEqual(200, response.status_code, 'To long of a valid sidecar has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid sidecar should convert to long successfully")
            self.assertTrue(response.data, "The converted to long sidecar should not be empty")

    def test_sidecars_results_to_long_invalid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_TO_LONG,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events_bad.json"),
                          bc.CHECK_FOR_WARNINGS: 'on'}

            response = self.app.test.post('/sidecars_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'sidecars_submit should return a Response when invalid to long sidecar')
            self.assertEqual(200, response.status_code, 'Conversion of an invalid sidecar to long has valid status')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "Conversion of an invalid sidecar to long generates a warning")
            self.assertTrue(response.data,
                            "The response data for invalid conversion to long should have error messages")

    def test_sidecars_results_to_short_valid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: 'Other',
                          bc.SCHEMA_PATH: self._get_file_buffer("HED8.0.0.xml"),
                          bc.COMMAND_OPTION: bc.COMMAND_TO_SHORT,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/sidecars_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'sidecar_submit should return a Response when valid to short sidecar')
            self.assertEqual(200, response.status_code, 'To short of a valid sidecar has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid sidecar should convert to short successfully")
            self.assertTrue(response.data, "The converted to short sidecar should not be empty")

    def test_sidecars_results_validate_valid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.0.0',
                          bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/sidecars_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'sidecars_submit should return a Response when valid sidecar')
            self.assertEqual(200, response.status_code, 'Validation of a valid sidecar has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid sidecar should validate successfully")
            self.assertFalse(response.data, "The response for validated sidecar should be empty")

    def test_sidecars_results_validate_valid_other(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: 'Other',
                          bc.SCHEMA_PATH: self._get_file_buffer("HED8.0.0.xml"),
                          bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/sidecars_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'sidecars_submit should return a Response when valid sidecar')
            self.assertEqual(200, response.status_code, 'Validation of a valid sidecar has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid sidecar should validate successfully")
    #         self.assertFalse(response.data, "The response for validated sidecar should be empty")

    def test_sidecars_results_to_short_invalid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_TO_SHORT,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events_bad.json"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/sidecars_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'sidecars_submit should return a response object when invalid to short sidecar')
            self.assertEqual(200, response.status_code, 'Conversion of invalid sidecar to short has valid status')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "Conversion of an invalid sidecar to short generates a warning")
            self.assertTrue(response.data,
                            "The response data for invalid conversion to short should have error messages")

    def test_sidecars_results_validate_invalid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events_bad.json"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/sidecars_submit', content_type='multipart/form-data',
                                          data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'sidecars_submit validate should return a response object when invalid sidecar')
            self.assertEqual(200, response.status_code,
                             'Validation of an invalid sidecar to short has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "Validation of an invalid sidecar to short generates a warning")
            self.assertTrue(response.data,
                            "The response data for invalid validation should have error messages")


if __name__ == '__main__':
    unittest.main()
