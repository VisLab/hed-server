import os
import requests
from tests_services.test_services_base import ServicesTest


class SidecarTests(ServicesTest):
    def test_validate_valid_json_sidecar(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "sidecar_validate",
            "schema_version": "8.2.0",
            "sidecar_string": self.data['jsonText'],
            "check_for_warnings": True
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data['error_type'])
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_validate_invalid_json_sidecar(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "sidecar_validate",
            "schema_url": self.data['schemaUrl'],
            "sidecar_string": self.data['jsonBadText'],
            "check_for_warnings": True
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertNotEqual(response_data['results']['msg_category'], 'success')

    def test_convert_json_sidecar_to_long(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "sidecar_to_long",
            "schema_string": self.data['schemaText'],
            "sidecar_string": self.data['jsonText'],
            "expand_defs": False
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_convert_json_sidecar_to_short(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "sidecar_to_short",
            "schema_version": "8.2.0",
            "sidecar_string": self.data['jsonText'],
            "expand_defs": True
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_extract_spreadsheet_from_json_sidecar(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "sidecar_extract_spreadsheet",
            "sidecar_string": self.data['jsonText']
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_merge_spreadsheet_with_json_sidecar(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "sidecar_merge_spreadsheet",
            "sidecar_string": "",
            "spreadsheet_string": self.data['spreadsheetTextExtracted']
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['results']['msg_category'], 'success')
