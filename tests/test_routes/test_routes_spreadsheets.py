import unittest

from flask import Response

from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_spreadsheets_results_empty_data(self):
        response = self.app.test.post("/spreadsheets_submit")
        self.assertEqual(
            200,
            response.status_code,
            "HED spreadsheet request succeeds even when no data",
        )
        self.assertTrue(
            isinstance(response, Response),
            "spreadsheets_submit to short should return a Response when no data",
        )
        header_dict = dict(response.headers)
        self.assertEqual(
            "error",
            header_dict["Category"],
            "The header msg_category when no spreadsheet is error ",
        )
        self.assertFalse(response.data, "The response data for empty spreadsheet request is empty")

    def test_spreadsheets_results_validate_valid(self):
        with self.app.app_context():
            input_data = {
                bc.SCHEMA_VERSION: "8.0.0",
                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                bc.WORKSHEET_NAME: "LKT 8HED3",
                bc.WORKSHEET_SELECTED: "LKT 8HED3",
                "column_4_use": "on",
                "column_4_name": "HED tags",
                bc.SPREADSHEET_FILE: self._get_file_buffer("ExcelMultipleSheets.xlsx"),
                bc.CHECK_FOR_WARNINGS: "on",
            }
            response = self.app.test.post(
                "/spreadsheets_submit",
                content_type="multipart/form-data",
                data=input_data,
            )
            self.assertTrue(
                isinstance(response, Response),
                "spreadsheets_submit should return a Response when valid dictionary",
            )
            self.assertEqual(
                200,
                response.status_code,
                "Validation of a valid dictionary has a valid status code",
            )
            headers_dict = dict(response.headers)
            self.assertEqual(
                "success",
                headers_dict["Category"],
                "The valid spreadsheet should validate successfully",
            )
            self.assertFalse(response.data, "The response for validated spreadsheet should be empty")

    def test_results_validate_invalid(self):
        with self.app.app_context():
            input_data = {
                bc.SCHEMA_VERSION: "8.2.0",
                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                bc.WORKSHEET_NAME: "LKT Events",
                bc.WORKSHEET_SELECTED: "LKT Events",
                "column_4_use": "on",
                "column_4_name": "HED tags",
                bc.SPREADSHEET_FILE: self._get_file_buffer("ExcelMultipleSheets.xlsx"),
                bc.CHECK_FOR_WARNINGS: "on",
            }
            response = self.app.test.post(
                "/spreadsheets_submit",
                content_type="multipart/form-data",
                data=input_data,
            )
            self.assertTrue(
                isinstance(response, Response),
                "spreadsheet_submit validate should return a response object when invalid spreadsheet",
            )
            self.assertEqual(
                200,
                response.status_code,
                "Validation of an invalid spreadsheet to short has a valid status code",
            )
            headers_dict = dict(response.headers)
            self.assertEqual(
                "warning",
                headers_dict["Category"],
                "Validation of an invalid spreadsheet to short generates a warning",
            )
            self.assertTrue(
                response.data,
                "The response data for invalid validation should have error messages",
            )

    def test_spreadsheets_results_convert_to_long_valid(self):
        with self.app.app_context():
            input_data = {
                bc.SCHEMA_VERSION: "8.0.0",
                bc.COMMAND_OPTION: bc.COMMAND_TO_LONG,
                bc.WORKSHEET_NAME: "LKT 8HED3",
                bc.WORKSHEET_SELECTED: "LKT 8HED3",
                "column_4_use": "on",
                "column_4_name": "HED tags",
                bc.SPREADSHEET_FILE: self._get_file_buffer("ExcelMultipleSheets.xlsx"),
            }
            response = self.app.test.post(
                "/spreadsheets_submit",
                content_type="multipart/form-data",
                data=input_data,
            )
            self.assertIsInstance(response, Response, "spreadsheets_submit to_long should return a Response")
            self.assertEqual(200, response.status_code, "To long conversion should return status 200")
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"], "Valid spreadsheet to_long should succeed")
            self.assertTrue(response.data, "Converted spreadsheet should not be empty")

    def test_spreadsheets_results_convert_to_short_valid(self):
        with self.app.app_context():
            input_data = {
                bc.SCHEMA_VERSION: "8.0.0",
                bc.COMMAND_OPTION: bc.COMMAND_TO_SHORT,
                bc.WORKSHEET_NAME: "LKT 8HED3",
                bc.WORKSHEET_SELECTED: "LKT 8HED3",
                "column_4_use": "on",
                "column_4_name": "HED tags",
                bc.SPREADSHEET_FILE: self._get_file_buffer("ExcelMultipleSheets.xlsx"),
            }
            response = self.app.test.post(
                "/spreadsheets_submit",
                content_type="multipart/form-data",
                data=input_data,
            )
            self.assertIsInstance(response, Response, "spreadsheets_submit to_short should return a Response")
            self.assertEqual(200, response.status_code, "To short conversion should return status 200")
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"], "Valid spreadsheet to_short should succeed")
            self.assertTrue(response.data, "Converted spreadsheet should not be empty")


if __name__ == "__main__":
    unittest.main()
