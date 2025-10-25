import json
import unittest

from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_schemas_results_empty_data(self):
        result = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data={})
        self.assertEqual(200, result.status_code, 'HED schemas request succeeds even when no data')
        headers_dict = dict(result.headers)
        self.assertTrue(headers_dict, "The error message still has a header")
        response = json.loads(result.data.decode('utf-8'))
        self.assertEqual("error", response['msg_category'], 'An empty request produces an error')
        self.assertFalse(response["data"], "The response data for empty schema request is empty")

    def test_schemas_results_convert_mediawiki_invalid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'convert',
                          bc.SCHEMA_FILE: self._get_file_buffer("HEDBad8.0.0.mediawiki"),
                          'check_for_warnings': 'on'}
            result = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, result.status_code, 'Convert of a invalid mediawiki has a response')
            headers_dict = dict(result.headers)
            self.assertTrue(headers_dict, "The error message still has a header")
            response = json.loads(result.data.decode('utf-8'))
            self.assertEqual("error", response['msg_category'], 'An invalid schema produces an error')
            self.assertFalse(response["data"], "The response data for invalid schema  is empty")

    def test_schemas_results_convert_mediawiki_valid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'convert_schema',
                          bc.SCHEMA_FILE: self._get_file_buffer("HED8.2.0.mediawiki"),
                          'check_for_warnings': 'on'}
            result = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, result.status_code, 'Convert of a valid mediawiki has a response')
            headers_dict = dict(result.headers)
            self.assertTrue(headers_dict, "A successful conversion has a header")
            response = json.loads(result.data.decode('utf-8'))
            self.assertEqual("success", response['msg_category'], 'An valid schema')
            self.assertTrue(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['output_display_name'], 'HED8.2.0_converted.zip',)

    def test_schemas_results_convert_xml_valid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'convert_schema',
                          bc.SCHEMA_FILE: self._get_file_buffer("HED8.2.0.xml"),
                          'check_for_warnings': 'on'}
            result = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, result.status_code, 'Convert of a valid xml has a response')
            headers_dict = dict(result.headers)
            self.assertTrue(headers_dict, "A successful conversion has a header")
            response = json.loads(result.data.decode('utf-8'))
            self.assertEqual("success", response['msg_category'], 'An valid schema')
            self.assertTrue(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['output_display_name'], 'HED8.2.0_converted.zip' )

    def test_schemas_results_convert_xml_url_valid(self):
        schema_url = \
            'https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml'
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_url_option',
                          'command_option': 'convert_schema',
                          'schema_url': schema_url,
                          'check_for_warnings': 'on'}
            result = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200,result.status_code, 'Conversion of a valid xml url has a response')
            headers_dict = dict(result.headers)
            self.assertTrue(headers_dict, "A successful conversion has a header")
            response = json.loads(result.data.decode('utf-8'))
            self.assertEqual("success", response['msg_category'], 'An valid schema')
            self.assertTrue(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['output_display_name'], 'HED8.2.0_converted.zip')

    def test_schemas_results_convert_xml_url_valid2(self):
        schema_url = \
            'https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml'
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_url_option',
                          'command_option': 'convert_schema',
                          'schema_url': schema_url,
                          'check_for_warnings': 'on'}
            result = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, result.status_code, 'Conversion of a valid xml url has a response')
            headers_dict = dict(result.headers)
            self.assertTrue(headers_dict, "A successful conversion has a header")
            response = json.loads(result.data.decode('utf-8'))
            self.assertEqual("success", response['msg_category'], 'An valid schema')
            self.assertTrue(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['output_display_name'], 'HED8.2.0_converted.zip')

    def test_schemas_results_validate_mediawiki_invalid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'validate',
                          'schema_file': "",
                          'check_for_warnings': 'on'}
            results = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, results.status_code, 'Validation of a invalid mediawiki has a response')
            headers_dict = dict(results.headers)
            self.assertTrue(headers_dict, "An unsuccessful validation has a header")
            response = json.loads(results.data.decode('utf-8'))
            self.assertEqual("error", response['msg_category'], 'An invalid schema')
            self.assertFalse(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['msg'], 'SCHEMA_NOT_FOUND:  [Must provide a source schema]')


    def test_schemas_results_validate_mediawiki_valid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'validate',
                          bc.SCHEMA_FILE: self._get_file_buffer("HED8.2.0.mediawiki"),
                          'check_for_warnings': 'on'}
            results = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, results.status_code, 'Validation of a valid mediawiki has a response')
            headers_dict = dict(results.headers)
            self.assertTrue(headers_dict, "A successful validation has a header")
            response = json.loads(results.data.decode('utf-8'))
            self.assertEqual("success", response['msg_category'], 'An valid schema')
            self.assertFalse(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['msg'], 'Schema had no validation issues')

    def test_schemas_results_validate_xml_valid(self):
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_file_option',
                          'command_option': 'validate',
                          bc.SCHEMA_FILE: self._get_file_buffer("HED8.2.0.xml"),
                          'check_for_warnings': 'on'}
            results = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, results.status_code, 'Validation of a valid xml has a response')
            headers_dict = dict(results.headers)
            self.assertTrue(headers_dict, "An unsuccessful conversion has a header")
            response = json.loads(results.data.decode('utf-8'))
            self.assertEqual("success", response['msg_category'], 'An valid schema')
            self.assertFalse(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['msg'], 'Schema had no validation issues')

    def test_schemas_results_validate_xml_url_invalid(self):
        schema_url = 'https://raw.githubusercontent.com/hed-standard/hed-schemas/' + \
                     'main/standard_schema/hedxml/deprecated/HED7.2.0.xml'
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_url_option',
                          'command_option': 'validate',
                          'schema_url': schema_url,
                          'check_for_warnings': 'on'}
            results = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, results.status_code, 'Validation of a valid xml url has a response')
            headers_dict = dict(results.headers)
            self.assertTrue(headers_dict, "An unsuccessful validation has a header")
            response = json.loads(results.data.decode('utf-8'))
            self.assertEqual("error", response['msg_category'], 'An invalid schema')
            self.assertFalse(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['msg'], 'INVALID_HED_FORMAT: HED7.2.0 [Attempting to load an outdated or invalid XML schema]')

def test_schemas_results_validate_xml_url_valid(self):
        schema_url = \
            'https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml'
        with self.app.app_context():
            input_data = {'schema_upload_options': 'schema_url_option',
                          'command_option': 'validate',
                          'schema_url': schema_url,
                          'check_for_warnings': 'on'}
            results = self.app.test.post('/schemas_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, results.status_code, 'Validation of a valid xml url has a response')
            response = json.loads(results.data.decode('utf-8'))
            self.assertEqual("success", response['msg_category'], 'An valid schema')
            self.assertFalse(response["data"], "The response data for valid schema is not empty")
            self.assertEqual(response['msg'], 'Schema had no validation issues')


if __name__ == '__main__':
    unittest.main()
