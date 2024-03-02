import requests
from tests_services.test_services_base import ServicesTest


class TestEventSearchServices(ServicesTest):

    def test_search_events_valid_query(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_search",
            "schema_version": "8.2.0",
            "events_string": self.data['eventsText'],
            "sidecar_string": self.data['jsonText'],
            "queries": ['Intended-effect, Cue'],
            "expand_defs": True
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')

    def test_search_events_with_additional_columns(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "events_search",
            "schema_version": "8.2.0",
            "events_string": self.data['eventsText'],
            "sidecar_string": self.data['jsonText'],
            "queries": ['Intended-effect, Cue', 'Sensory-event'],
            "expand_defs": True
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get('error_type'))
        self.assertEqual(response_data['results']['msg_category'], 'success')