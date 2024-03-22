import requests
from tests_services.test_services_base import ServicesTest


class TestEventServices(ServicesTest):

    def test_validate_valid_events_file(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_validate",
            "schema_version": "8.2.0",
            "events_string": self.data['eventsText'],
            "sidecar_string": self.data['jsonText'],
            "check_for_warnings": False
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_validate_invalid_events_file(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_validate",
            "schema_version": "8.2.0",
            "events_string": self.data['eventsText'],
            "sidecar_string": self.data['jsonBadText'],
            "check_for_warnings": True
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertNotEqual(response_data['results']['msg_category'], 'success')

    def test_assemble_valid_events_file(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_assemble",
            "schema_version": "8.2.0",
            "events_string": self.data['eventsText'],
            "sidecar_string": self.data['jsonText'],
            "expand_defs": False
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_assemble_events_file_expand_defs(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_assemble",
            "schema_version": "8.2.0",
            "events_string": self.data['eventsText'],
            "sidecar_string": self.data['jsonText'],
            "expand_defs": True
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_generate_sidecar_template_from_events_file(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_generate_sidecar",
            "events_string": self.data['eventsText'],
            "columns_skip": ['onset', 'duration', 'sample'],
            "columns_value": ['trial', 'rep_lag', 'stim_file']
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')