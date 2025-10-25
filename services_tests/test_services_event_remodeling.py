import requests

from services_tests.test_services_base import ServicesTest


class TestEventRemodelingServices(ServicesTest):
    def test_remodel_events_by_removing_columns(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_remodel",
            "remodel_string": self.data['remodelRemoveColumnsText'],
            "events_string": self.data['eventsText']
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_remodel_events_by_summarizing_columns(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_remodel",
            "remodel_string": self.data['remodelSummarizeColumnsText'],
            "events_string": self.data['eventsText']
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_summarize_files_including_hed(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_remodel",
            "schema_version": "8.2.0",
            "remodel_string": self.data['remodelSummarizeColumnsText'],
            "events_string": self.data['eventsText'],
            "sidecar_string": self.data['jsonText']
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_factor_hed_types(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_remodel",
            "schema_version": "8.2.0",
            "remodel_string": self.data['remodelFactorTypesText'],
            "events_string": self.data['eventsText'],
            "sidecar_string": self.data['jsonText']
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')
