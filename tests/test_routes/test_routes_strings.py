import json
import unittest
from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):

    def test_strings_results_empty_data(self):
        response = self.app.test.post('/strings_submit')
        self.assertEqual(200, response.status_code, 'HED string request succeeds even when no data')
        self.assertTrue(response.data, "The returned data for empty string question is not empty")
        response_dict = json.loads(response.data)
        self.assertIsInstance(response_dict, dict, "The empty string response data is returned in a dictionary")
        self.assertTrue(response_dict["message"], "The empty string response message is not empty")

    def test_strings_results_to_long(self):
        with self.app.app_context():
            test_string = 'Property/Sensory-property/Sensory-attribute/Visual-attribute/Color/CSS-color/Red-color/Red'
            input_data = {bc.SCHEMA_VERSION: '8.0.0',
                          bc.COMMAND_OPTION: bc.COMMAND_TO_LONG,
                          bc.CHECK_FOR_WARNINGS: 'on',
                          bc.STRING_INPUT: test_string}

            response = self.app.test.post('/strings_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'To long of a long string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("success", response_dict["msg_category"], "The long string should convert successfully")
            self.assertEqual(test_string, response_dict["data"][0],
                             "The long string should be unchanged after conversion to long")

            input_data["string_input"] = 'Red'
            response = self.app.test.post('/strings_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'To long of a short valid string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("success", response_dict["msg_category"], "The list should convert successfully")
            self.assertEqual(test_string, response_dict["data"][0],
                             "The converted short string should be in long form when converted")

            input_data["string_input"] = 'Blob,Blue,Label/3'
            response = self.app.test.post('/strings_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Conversion of an invalid string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("warning", response_dict["msg_category"],
                             "Invalid hed string conversion to long generates a warning")
            self.assertTrue(response_dict["data"][0], "The data of a to long error should have error messages")

    def test_strings_results_to_short(self):
        with self.app.app_context():
            test_string = 'Property/Sensory-property/Sensory-attribute/Visual-attribute/Color/CSS-color/Red-color/Red'
            input_data = {bc.SCHEMA_VERSION: '8.0.0',
                          bc.COMMAND_OPTION: bc.COMMAND_TO_SHORT,
                          bc.CHECK_FOR_WARNINGS: 'on',
                          bc.STRING_INPUT: test_string}

            response = self.app.test.post('/strings_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'To short of a long string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("success", response_dict["msg_category"],
                             "To short conversion of a long string is success")
            self.assertEqual("Red", response_dict["data"][0], "The converted long string should be in the short form")

            input_data["string_input"] = 'Red'
            response = self.app.test.post('/strings_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'To short of a short valid string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("success", response_dict["msg_category"], "To short conversion of short string is success")
            self.assertEqual(input_data["string_input"], response_dict["data"][0],
                             "The converted short string should be in short form")

            input_data["string_input"] = 'Blob,Blue,Label/3'
            response = self.app.test.post('/strings_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'To short of an invalid string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("warning", response_dict["msg_category"],
                             "To short of invalid string generates a warning")
            self.assertTrue(response_dict["data"][0], "The data should have error messages")

    def test_strings_results_validate(self):
        with self.app.app_context():
            response = self.app.test.post('/strings_submit', content_type='multipart/form-data',
                                          data={bc.SCHEMA_VERSION: '8.0.0',
                                                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                                                bc.CHECK_FOR_WARNINGS: 'on',
                                                bc.STRING_INPUT: 'Red,Blue,Label/3'})

            self.assertEqual(200, response.status_code, 'Validation of a valid string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("success", response_dict["msg_category"], "The list should validate successfully")
            self.assertFalse(response_dict["data"], "No data should be returned if validation successful")

            response = self.app.test.post('/strings_submit', content_type='multipart/form-data',
                                          data={bc.SCHEMA_VERSION: '8.0.0',
                                                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                                                bc.CHECK_FOR_WARNINGS: 'on',
                                                bc.STRING_INPUT: 'Blob,Blue,Label/3'})
            self.assertEqual(200, response.status_code, 'Validation of an invalid string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("warning", response_dict["msg_category"],
                             "Invalid hed string validation generates a warning")
            self.assertTrue(response_dict["data"], "The data should have error messages")

    def test_strings_results_validate_defs(self):
        with self.app.app_context():
            response = self.app.test.post('/strings_submit', content_type='multipart/form-data',
                                          data={bc.SCHEMA_VERSION: '8.2.0',
                                                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                                                bc.CHECK_FOR_WARNINGS: 'on',
                                                bc.STRING_INPUT: 'Def/TestDef/13',
                                                # bc.DEFINITION_FILE: (def_data, 'def_test.json'),
                                                bc.DEFINITION_FILE: self._get_file_buffer("def_test.json")
                                                })

            self.assertEqual(200, response.status_code, 'Validation of a valid string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("success", response_dict["msg_category"], "The list should validate successfully")
            self.assertFalse(response_dict["data"], "No data should be returned if validation successful")

            response = self.app.test.post('/strings_submit', content_type='multipart/form-data',
                                          data={bc.SCHEMA_VERSION: '8.2.0',
                                                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                                                bc.CHECK_FOR_WARNINGS: 'on',
                                                bc.STRING_INPUT: 'Def/TestDef/13'})
            self.assertEqual(200, response.status_code, 'Validation of an invalid string has a response')
            response_dict = json.loads(response.data)
            self.assertEqual("warning", response_dict["msg_category"],
                             "No Definition provided, so should produce an error")
            self.assertTrue(response_dict["data"], "The data should have error messages")


if __name__ == '__main__':
    unittest.main()
