import unittest
from flask import Response
from hedweb.constants import base_constants
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_spreadsheets_results_empty_data(self):
        response = self.app.test.post('/spreadsheets_submit')
        self.assertEqual(200, response.status_code, 'HED spreadsheet request succeeds even when no data')
        self.assertTrue(isinstance(response, Response),
                        'spreadsheets_submit to short should return a Response when no data')
        header_dict = dict(response.headers)
        self.assertEqual("error", header_dict["Category"], "The header msg_category when no spreadsheet is error ")
        self.assertFalse(response.data, "The response data for empty spreadsheet request is empty")

    def test_spreadsheets_results_validate_valid(self):
        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.0.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_VALIDATE,
                          base_constants.WORKSHEET_NAME: 'LKT 8HED3',
                          base_constants.WORKSHEET_SELECTED: 'LKT 8HED3',
                          base_constants.HAS_COLUMN_NAMES: 'on',
                          'column_4_check': 'on',
                          base_constants.SPREADSHEET_FILE: self._get_file_buffer("ExcelMultipleSheets.xlsx"),
                          base_constants.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/spreadsheets_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'spreadsheets_submit should return a Response when valid dictionary')
            self.assertEqual(200, response.status_code, 'Validation of a valid dictionary has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid spreadsheet should validate successfully")
            self.assertFalse(response.data, "The response for validated spreadsheet should be empty")

    def test_results_validate_invalid(self):
        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.0.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_VALIDATE,
                          base_constants.WORKSHEET_NAME: 'LKT Events',
                          base_constants.WORKSHEET_SELECTED: 'LKT Events',
                          'column_4_check': 'on',
                          base_constants.SPREADSHEET_FILE: self._get_file_buffer("ExcelMultipleSheets.xlsx"),
                          base_constants.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/spreadsheets_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'spreadsheet_submit validate should return a response object when invalid spreadsheet')
            self.assertEqual(200, response.status_code,
                             'Validation of an invalid spreadsheet to short has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "Validation of an invalid spreadsheet to short generates a warning")
            self.assertTrue(response.data,
                            "The response data for invalid validation should have error messages")


if __name__ == '__main__':
    unittest.main()
