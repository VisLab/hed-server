
import json

from hedweb.constants import base_constants
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_submit_service_spreadsheets_validate_route(self):
        with self.app.app_context():
            json_data = {base_constants.CHECK_FOR_WARNINGS: 'on',
                         base_constants.SCHEMA_VERSION: '8.0.0',
                         base_constants.SPREADSHEET_STRING: self._get_file_string("LKTEventCodesHED3.tsv"),
                         # 'column_4_check': 'on',
                         base_constants.SERVICE: 'spreadsheet_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json', data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertEqual('success', results['msg_category'], "should give success when no errors")
            self.assertFalse(results["data"], 'process not return data no no errors')

    def test_submit_service_spreadsheets_validate_route_file_invalid(self):
        with self.app.app_context():
            json_data = {base_constants.CHECK_FOR_WARNINGS: 'on',
                         base_constants.SCHEMA_VERSION: '8.2.0',
                         base_constants.SPREADSHEET_STRING: "BAD FILE",
                         'column_4_check': 'on',
                         base_constants.SERVICE: 'spreadsheet_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json', data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            had_error = json_data2.get("error_type")
            self.assertTrue(had_error)

    def test_submit_service_spreadsheets_validate_route_file_issues(self):
        with self.app.app_context():
            json_data = {base_constants.CHECK_FOR_WARNINGS: 'on',
                         base_constants.SCHEMA_VERSION: '8.2.0',
                         base_constants.SPREADSHEET_STRING: self._get_file_string("LKTEventCodesHED3.tsv"),
                         'column_4_check': 'on',
                         base_constants.SERVICE: 'spreadsheet_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json', data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertTrue('data' in results,'should have a data key when no errors')
            self.assertEqual('warning', results["msg_category"], 'should be warning when errors')

    def test_submit_service_spreadsheets_validate_with_defs(self):
        with self.app.app_context():
            json_data = {base_constants.CHECK_FOR_WARNINGS: 'on',
                         base_constants.SCHEMA_VERSION: '8.2.0',
                         base_constants.SPREADSHEET_STRING: self._get_file_string("spreadsheet_with_defs.tsv"),
                         base_constants.DEFINITION_STRING: self._get_file_string("def_test.json"),
                         'column_2_check': 'on',
                         base_constants.SERVICE: 'spreadsheet_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json', data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertEqual('success', results['msg_category'], "should give success when no errors")
            self.assertFalse(results["data"], 'process not return data no no errors')

    def test_submit_service_spreadsheets_validate_with_defs_missing(self):
        with self.app.app_context():
            json_data = {base_constants.CHECK_FOR_WARNINGS: 'on',
                         base_constants.SCHEMA_VERSION: '8.2.0',
                         base_constants.SPREADSHEET_STRING: self._get_file_string("spreadsheet_with_defs.tsv"),
                         'column_2_check': 'on',
                         base_constants.SERVICE: 'spreadsheet_validate'}

            response = self.app.test.post('/services_submit', content_type='application/json', data=json.dumps(json_data))
            json_data2 = json.loads(response.data)
            results = json_data2['results']
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertTrue('data' in results,'should have a data key when no errors')
            self.assertEqual('warning', results["msg_category"], 'should be warning when errors')