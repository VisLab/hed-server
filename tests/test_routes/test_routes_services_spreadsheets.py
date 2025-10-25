import json

from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_submit_service_spreadsheets_validate_route(self):
        with self.app.app_context():
            json_data = {
                bc.CHECK_FOR_WARNINGS: True,
                bc.SCHEMA_VERSION: "8.2.0",
                bc.SPREADSHEET_STRING: self._get_file_string("LKTEventCodesHED3.tsv"),
                bc.TAG_COLUMNS: [4],
                bc.SERVICE: "spreadsheet_validate",
            }

            response = self.app.test.post(
                "/services_submit",
                content_type="application/json",
                data=json.dumps(json_data),
            )
            json_data2 = json.loads(response.data)
            results = json_data2["results"]
            self.assertTrue(
                isinstance(results, dict),
                "should return a dictionary when validation errors",
            )
            self.assertEqual(
                "warning", results["msg_category"], "should give warning when errors"
            )
            self.assertTrue(results["data"], "process not return data no no errors")

    def test_submit_service_spreadsheets_validate_route_file_invalid(self):
        with self.app.app_context():
            json_data = {
                bc.CHECK_FOR_WARNINGS: "on",
                bc.SCHEMA_VERSION: "8.2.0",
                bc.SPREADSHEET_STRING: "BAD FILE",
                bc.TAG_COLUMNS: [3],
                bc.SERVICE: "spreadsheet_validate",
            }

            response = self.app.test.post(
                "/services_submit",
                content_type="application/json",
                data=json.dumps(json_data),
            )
            json_data2 = json.loads(response.data)
            results = json_data2["results"]
            self.assertEqual(
                "success", results["msg_category"], "ignores missing columns"
            )

    def test_submit_service_spreadsheets_validate_route_file_issues(self):
        with self.app.app_context():
            json_data = {
                bc.CHECK_FOR_WARNINGS: "on",
                bc.SCHEMA_VERSION: "8.2.0",
                bc.SPREADSHEET_STRING: self._get_file_string("LKTEventCodesHED3.tsv"),
                bc.TAG_COLUMNS: [3],
                bc.SERVICE: "spreadsheet_validate",
            }

            response = self.app.test.post(
                "/services_submit",
                content_type="application/json",
                data=json.dumps(json_data),
            )
            json_data2 = json.loads(response.data)
            results = json_data2["results"]
            self.assertTrue("data" in results, "should have a data key when no errors")
            self.assertEqual(
                "warning", results["msg_category"], "should be warning when errors"
            )

    def test_submit_service_spreadsheets_validate_with_defs(self):
        with self.app.app_context():
            json_data = {
                bc.CHECK_FOR_WARNINGS: "on",
                bc.SCHEMA_VERSION: "8.2.0",
                bc.SPREADSHEET_STRING: self._get_file_string(
                    "spreadsheet_with_defs.tsv"
                ),
                bc.DEFINITION_STRING: self._get_file_string("def_test.json"),
                bc.TAG_COLUMNS: [2],
                bc.SERVICE: "spreadsheet_validate",
            }

            response = self.app.test.post(
                "/services_submit",
                content_type="application/json",
                data=json.dumps(json_data),
            )
            json_data2 = json.loads(response.data)
            results = json_data2["results"]
            self.assertTrue(
                isinstance(results, dict),
                "should return a dictionary when validation errors",
            )
            self.assertEqual(
                "success", results["msg_category"], "should give success when no errors"
            )
            self.assertFalse(results["data"], "process not return data no no errors")

    def test_submit_service_spreadsheets_validate_with_defs_missing(self):
        with self.app.app_context():
            json_data = {
                bc.CHECK_FOR_WARNINGS: True,
                bc.SCHEMA_VERSION: "8.2.0",
                bc.SPREADSHEET_STRING: self._get_file_string(
                    "spreadsheet_with_defs.tsv"
                ),
                bc.TAG_COLUMNS: [2],
                bc.SERVICE: "spreadsheet_validate",
            }

            response = self.app.test.post(
                "/services_submit",
                content_type="application/json",
                data=json.dumps(json_data),
            )
            json_data2 = json.loads(response.data)
            results = json_data2["results"]
            self.assertTrue(
                isinstance(results, dict),
                "should return a dictionary when validation errors",
            )
            self.assertTrue("data" in results, "should have a data key when no errors")
            self.assertEqual(
                "warning", results["msg_category"], "should be warning when errors"
            )
