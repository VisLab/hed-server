import unittest
from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_schemas_results_empty_data(self):
        response = self.app.test.post('/schemas_submit')
        self.assertEqual(200, response.status_code, 'HED schemas request succeeds even when no data')
        header_dict = dict(response.headers)
        self.assertEqual("error", header_dict["Category"],
                         "The header msg_category when no schema request data is error ")
        self.assertFalse(response.data, "The response data for empty schema request is empty")

    def test_schemas_results_convert_mediawiki_invalid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'convert',
                          bc.SCHEMA_FILE: self._get_file_buffer("HEDBad8.0.0.mediawiki"),
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Convert of a invalid mediawiki has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("error", headers_dict["Category"],
                             "The mediawiki schema does not load -- validate and correct errors before converting.")
            self.assertFalse(response.data, "The response data for a fully invalid media wiki should be empty")
            self.assertTrue(headers_dict['Message'],
                            "The error message for invalid mediawiki conversion should not be empty")

    def test_schemas_results_convert_mediawiki_valid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'convert_schema',
                          bc.SCHEMA_FILE: self._get_file_buffer("HED8.2.0.mediawiki"),
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Convert of a valid mediawiki has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid mediawiki should convert to xml successfully")
            self.assertTrue(response.data, "The converted schema should not be empty")
            self.assertEqual('attachment filename=HED8.2.0.xml',
                             headers_dict['Content-Disposition'], "Convert of valid mediawiki should return xml")

    def test_schemas_results_convert_xml_valid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'convert_schema',
                          bc.SCHEMA_FILE: self._get_file_buffer("HED8.2.0.xml"),
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Convert of a valid xml has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid xml should validate successfully")
            self.assertTrue(response.data, "The validated schema should not be empty")
            self.assertEqual('attachment filename=HED8.2.0.mediawiki',
                             headers_dict['Content-Disposition'],
                             "Validation of valid xml should not return a file")

    def test_schemas_results_convert_xml_url_valid(self):
        schema_url = \
            'https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml'
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_url_option',
                          'command_option': 'convert_schema',
                          'schema_url': schema_url,
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Conversion of a valid xml url has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid xml url should convert to mediawiki successfully")
            self.assertTrue(response.data, "The converted xml url schema should not be empty")
            self.assertEqual('attachment filename=HED8.2.0.mediawiki',
                             headers_dict['Content-Disposition'], "Conversion of valid xml url should return mediawiki")

    def test_schemas_results_convert_xml_url_valid2(self):
        schema_url = \
            'https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml'
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_url_option',
                          'command_option': 'convert_schema',
                          'schema_url': schema_url,
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Conversion of a valid xml url has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid xml url should convert to mediawiki successfully")
            self.assertTrue(response.data, "The converted xml url schema should not be empty")
            self.assertEqual('attachment filename=HED8.2.0.mediawiki',
                             headers_dict['Content-Disposition'], "Conversion of valid xml url should return mediawiki")

    def test_schemas_results_validate_mediawiki_invalid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'validate',
                          'schema_file': "",
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Validation of a invalid mediawiki has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("error", headers_dict["Category"],
                             "A schema that cannot be loaded should return an error")
            self.assertFalse(response.data,
                             "The response data for a fully invalid mediawiki validation should be empty")
            self.assertTrue(headers_dict['Message'],
                            "The error message for invalid mediawiki conversion should not be empty")

    def test_schemas_results_validate_mediawiki_valid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'validate',
                          bc.SCHEMA_FILE: self._get_file_buffer("HED8.2.0.mediawiki"),
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Validation of a valid mediawiki has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid mediawiki should validate successfully")
            self.assertFalse(response.data, "The response data for validated mediawiki should be empty")
            self.assertEqual(None, headers_dict.get('Content-Disposition', None),
                             "Validation of valid mediawiki should not return a file")

    def test_schemas_results_validate_xml_valid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'validate',
                          bc.SCHEMA_FILE: self._get_file_buffer("HED8.2.0.xml"),
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Validation of a valid xml has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid xml should validate successfully")
            self.assertFalse(response.data, "The validated schema data should be empty")
            self.assertEqual(None, headers_dict.get('Content-Disposition', None),
                             "Validation of valid xml should return any response data")

    def test_schemas_results_validate_xml_url_invalid(self):
        schema_url = 'https://raw.githubusercontent.com/hed-standard/hed-schemas/' + \
                     'main/standard_schema/hedxml/deprecated/HED7.2.0.xml'
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_url_option',
                          'command_option': 'validate',
                          'schema_url': schema_url,
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Validation of a valid xml url has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("error", headers_dict["Category"],
                             "The xml url for 7.2.0 should not be 3G compliant")
            self.assertFalse(response.data, "The old schema is very invalid and should produce no issues.")

    def test_schemas_results_validate_xml_url_valid(self):
        schema_url = \
            'https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml'
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_url_option',
                          'command_option': 'validate',
                          'schema_url': schema_url,
                          'check_for_warnings': 'on'}
            response = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Validation of a valid xml url has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid xml url should be successful")
            self.assertFalse(response.data, "The validated xml url schema should return empty response data")
            self.assertEqual(None, headers_dict.get('Content-Disposition', None),
                             "Validation of valid xml url should not return an error file")


if __name__ == '__main__':
    unittest.main()
