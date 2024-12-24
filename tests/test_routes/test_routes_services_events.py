
import json

from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_submit_service_events_validate_route(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_VERSION: '8.2.0',
                         bc.EVENTS_STRING: self._get_file_string("bids_events.tsv"),
                         bc.SIDECAR_STRING: self._get_file_string("bids_events.json"),
                         bc.SERVICE: 'events_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json',
                                          data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertEqual('success', results['msg_category'], "should give success when no errors")
            self.assertFalse(results["data"], 'process not return data no no errors')

    def test_submit_service_events_validate_route_file_invalid(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_VERSION: '8.3.0',
                         bc.EVENTS_STRING: "bad file",
                         bc.SIDECAR_STRING: self._get_file_string("bids_events.json"),
                         bc.SERVICE: 'events_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json',
                                          data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2.get["results"]
            self.assertEqual('warning', results["msg_category"], 'should be warning when errors')

    def test_submit_service_events_validate_route_file_issues(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_VERSION: '8.2.0',
                         bc.EVENTS_STRING: self._get_file_string("bids_events.tsv"),
                         bc.SIDECAR_STRING: self._get_file_string("bids_events_bad.json"),
                         bc.SERVICE: 'events_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json',
                                          data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertEqual(results['msg_category'], 'warning', 'it should have warning')
            self.assertTrue('data' in results, 'should have a data key when no errors')

