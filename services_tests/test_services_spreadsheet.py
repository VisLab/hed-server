import requests
from services_tests.test_services_base import ServicesTest


class TestSpreadsheetServices(ServicesTest):
    def test_validate_valid_spreadsheet_file(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "spreadsheet_validate",
            "schema_version": "8.2.0",
            "spreadsheet_string": self.data['spreadsheetText'],
            "sidecar_string": self.data['jsonText'],
            "check_for_warnings": True,
            "tag_columns": [4]
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_validate_invalid_spreadsheet_file(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "spreadsheet_validate",
            "schema_version": "8.2.0",
            "spreadsheet_string": self.data['spreadsheetTextInvalid'],
            "check_for_warnings": True,
            "tag_columns": ["HED tags"]
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertNotEqual(response_data['results']['msg_category'], 'success')

    def test_convert_valid_spreadsheet_to_long(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "spreadsheet_to_long",
            "schema_string": self.data['schemaText'],
            "spreadsheet_string": self.data['spreadsheetText'],
            "expand_defs": True,
            "tag_columns": ["HED tags"]
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_convert_valid_spreadsheet_to_short(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "spreadsheet_to_short",
            "schema_string": self.data['schemaText'],
            "spreadsheet_string": self.data['spreadsheetText'],
            "expand_defs": True,
            "tag_columns": [4]
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')