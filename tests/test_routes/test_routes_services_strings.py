
import json
from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_submit_service_strings_validate_route(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_VERSION: '8.2.0',
                         bc.STRING_LIST: ["Event"],
                         bc.SERVICE: 'strings_validate'}

            response = self.app.test.post('/services_submit',
                                          content_type='application/json', data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertEqual('success', results['msg_category'], "should give success when no errors")
            self.assertFalse(results["data"], 'process not return data no no errors')

    def test_submit_service_strings_validate_route_file_invalid(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_VERSION: '8.2.0',
                         bc.STRING_LIST: ["Blech"],
                         bc.SERVICE: 'strings_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json',
                                          data=json.dumps(json_data))
            x = response.data
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertEqual('warning', results['msg_category'], "should give warning with issues")
            self.assertTrue(results["data"], 'process return data for issues')

    def test_submit_service_strings_validate_route_file_invalid_format(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_VERSION: '8.2.0',
                         bc.STRING_LIST: 'Blech',
                         bc.SERVICE: 'strings_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json',
                                          data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertEqual('warning', results['msg_category'], "should give warning with issues")
            self.assertTrue(results["data"], 'process return data for issues')
            self.assertEqual(len(results["data"]), 84, "Server is allowing a string as a string list input")
