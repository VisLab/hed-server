
import json

from hed.schema import load_schema_version, from_string

from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_submit_service_schema_validate_route(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_VERSION: '8.2.0', bc.SERVICE: 'schemas_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json',
                                          data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertEqual('success', results['msg_category'],
                             "schemas_validate services has success on HED8.2.0.xml")
            self.assertEqual(json.dumps('8.2.0'), results[bc.SCHEMA_VERSION], 'Version 8.2.0 was used')

    def test_submit_service_schema_validate_route_file(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_STRING: self._get_file_string("HEDBad8.0.0.mediawiki"),
                         bc.SERVICE: 'schemas_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json',
                                          data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            had_error = json_data2.get("error_type")
            self.assertTrue(had_error)

    def test_submit_service_schema_convert_route(self):
        with self.app.app_context():
            json_data = {bc.CHECK_FOR_WARNINGS: 'on',
                         bc.SCHEMA_VERSION: '8.2.0', bc.SERVICE: f"schemas_{bc.COMMAND_CONVERT_SCHEMA}"}

            results = self.app.test.post('/services_submit', content_type='application/json',
                                          data=json.dumps(json_data))
            self.assertEqual(200, results.status_code, 'Conversion of a valid xml url has a response')
            headers_dict = dict(results.headers)
            response = json.loads(results.data.decode('utf-8'))
            self.assertEqual("success", response["results"]['msg_category'], 'An valid schema')
            self.assertTrue(response["results"]["data"], "The response data for valid schema is not empty")
            self.assertEqual(response["results"]['msg'], 'Schema was successfully converted')


