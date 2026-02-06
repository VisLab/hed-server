import io
import json
import os
import unittest

from hed.errors.exceptions import HedFileError
from hed.models import Sidecar
from hed.schema import HedSchema, load_schema_version
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from hedweb.constants import base_constants as bc
from hedweb.process_service import ProcessServices
from tests.test_web_base import TestWebBase


class Test(TestWebBase):
    @staticmethod
    def get_request_template():
        return {
            "service": "",
            "schema_version": "",
            "schema_url": "",
            "schema_string": "",
            "sidecar_string": "",
            "events_string": "",
            "spreadsheet_string": "",
            "remodel_string": "",
            "columns_selected": "",
            "columns_categorical": "",
            "columns_value": "",
            "queries": "",
            "query_names": "",
            "check_for_warnings": False,
            "expand_context": True,
            "expand_defs": False,
            "include_summaries": False,
            "replace_defs": False,
            "include_prereleases": False,
        }

    def test_set_input_from_service_request_empty(self):
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                ProcessServices.process({})

    def test_set_input_from_service_request(self):
        with self.app.test:
            sidecar_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json"
            )
            with open(sidecar_path, "rb") as fp:
                sidecar_string = fp.read().decode("utf-8")
            json_data = {
                bc.SIDECAR_STRING: sidecar_string,
                bc.CHECK_FOR_WARNINGS: "on",
                bc.SCHEMA_VERSION: "8.2.0",
                bc.SERVICE: "sidecar_validate",
            }
            environ = create_environ(json=json_data)
            request = Request(environ)
            arguments = ProcessServices.set_input_from_request(request)
            self.assertIn(bc.SIDECAR, arguments, "should have a json sidecar")
            self.assertIsInstance(
                arguments[bc.SIDECAR], Sidecar, "should contain a sidecar"
            )
            self.assertIsInstance(
                arguments[bc.SCHEMA], HedSchema, "should have a HED schema"
            )
            self.assertEqual(
                "sidecar_validate",
                arguments[bc.SERVICE],
                "should have a service request",
            )
            self.assertTrue(
                arguments[bc.CHECK_FOR_WARNINGS],
                "should have check_warnings true when on",
            )

    def test_set_input_from_service_request_full_template(self):
        with self.app.test:
            sidecar_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json"
            )
            with open(sidecar_path, "rb") as fp:
                sidecar_string = fp.read().decode("utf-8")
            json_data = self.get_request_template()
            json_data[bc.SIDECAR_STRING] = sidecar_string
            json_data[bc.CHECK_FOR_WARNINGS] = (True,)
            json_data[bc.SCHEMA_VERSION] = ("8.2.0",)
            json_data[bc.SERVICE] = "sidecar_validate"
            environ = create_environ(json=json_data)
            request = Request(environ)
            arguments = ProcessServices.set_input_from_request(request)
            self.assertIn(bc.SIDECAR, arguments, "should have a json sidecar")
            self.assertIsInstance(
                arguments[bc.SIDECAR], Sidecar, "should contain a sidecar"
            )
            self.assertIsInstance(
                arguments[bc.SCHEMA], HedSchema, "should have a HED schema"
            )
            self.assertEqual(
                "sidecar_validate",
                arguments[bc.SERVICE],
                "should have a service request",
            )
            self.assertTrue(
                arguments[bc.CHECK_FOR_WARNINGS],
                "should have check_warnings true when on",
            )

    def test_set_column_parameters(self):
        from hedweb.process_service import ProcessServices

        arguments = {}
        params = {
            "columns_categorical": ["col1", "col2"],
            "columns_value": ["col3", "col4"],
        }
        ProcessServices.set_parameters(arguments, params)

        self.assertEqual(arguments[bc.COLUMNS_CATEGORICAL], ["col1", "col2"])
        self.assertEqual(arguments[bc.COLUMNS_VALUE], ["col3", "col4"])
        self.assertTrue(arguments[bc.HAS_COLUMN_NAMES])
        self.assertFalse(arguments[bc.TAG_COLUMNS])

    def test_services_set_sidecar(self):
        path_upper = (
            "data/eeg_ds003654s_hed_inheritance/task-FacePerception_events.json"
        )
        path_lower2 = "data/eeg_ds003654s_hed_inheritance/sub-002/sub-002_task-FacePerception_events.json"
        path_lower3 = "data/eeg_ds003654s_hed_inheritance/sub-003/sub-003_task-FacePerception_events.json"
        sidecar_path_upper = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), path_upper
        )
        sidecar_path_lower2 = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), path_lower2
        )
        sidecar_path_lower3 = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), path_lower3
        )

        with open(sidecar_path_upper) as f:
            data_upper = json.load(f)
        with open(sidecar_path_lower2) as f:
            data_lower2 = json.load(f)
        params2 = {bc.SIDECAR_STRING: [json.dumps(data_upper), json.dumps(data_lower2)]}
        arguments2 = {}
        ProcessServices.set_sidecar(arguments2, params2)
        self.assertIn(bc.SIDECAR, arguments2, "should have a sidecar")
        self.assertIsInstance(arguments2[bc.SIDECAR], Sidecar)
        sidecar2 = arguments2[bc.SIDECAR]
        self.assertIn("event_type", data_upper, "should have key event_type")
        self.assertNotIn("event_type", data_lower2, "should not have event_type")
        self.assertIn(
            "event_type", sidecar2.loaded_dict, "merged sidecar should have event_type"
        )

        with open(sidecar_path_lower3) as f:
            data_lower3 = json.load(f)
        params3 = {bc.SIDECAR_STRING: [json.dumps(data_upper), json.dumps(data_lower3)]}
        arguments3 = {}
        ProcessServices.set_sidecar(arguments3, params3)
        self.assertIn(bc.SIDECAR, arguments3, "should have a sidecar")
        self.assertIsInstance(arguments3[bc.SIDECAR], Sidecar)
        sidecar3 = arguments3[bc.SIDECAR]
        self.assertIn("event_type", data_upper, "should have key event_type")
        self.assertNotIn("event_type", data_lower3, "should have event_type")
        self.assertIn(
            "event_type", sidecar3.loaded_dict, "merged sidecar should have event_type"
        )

    def test_set_input_objects(self):
        sidecar_path = "data/task-FacePerception_events.json"
        sidecar_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), sidecar_path
        )

        sidecar = Sidecar(sidecar_path)

        events_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/sub-002_task-FacePerception_run-1_events.tsv",
        )
        with open(events_path) as fp:
            events_data = fp.read()

        from hed import HedString, SpreadsheetInput, TabularInput

        arguments = {
            bc.SCHEMA: load_schema_version("8.2.0"),
            bc.SIDECAR: sidecar,
            bc.TAG_COLUMNS: [4],
        }
        params = {
            bc.EVENTS_STRING: events_data,
            bc.SPREADSHEET_STRING: events_data,
            bc.STRING_LIST: ["Event", "Age"],
        }
        ProcessServices.set_input_objects(arguments, params)

        self.assertIsInstance(arguments[bc.EVENTS], TabularInput)
        self.assertIsInstance(arguments[bc.SPREADSHEET], SpreadsheetInput)
        self.assertEqual(len(arguments[bc.STRING_LIST]), 2)
        for item in arguments[bc.STRING_LIST]:
            self.assertIsInstance(item, HedString)

        # Raises error if tag columns not set, but it has a spreadsheet
        with self.assertRaises(KeyError):
            arguments = {}
            params = {
                bc.EVENTS_STRING: "",
                bc.SPREADSHEET_STRING: events_data,
            }
            ProcessServices.set_input_objects(arguments, params)

        arguments = {
            bc.SCHEMA: load_schema_version("8.2.0"),
            bc.SIDECAR: sidecar,
            bc.TAG_COLUMNS: [4],
        }
        params = {}
        ProcessServices.set_input_objects(arguments, params)

        self.assertNotIn(bc.EVENTS, arguments)
        self.assertNotIn(bc.SPREADSHEET, arguments)
        self.assertNotIn(bc.STRING_LIST, arguments)

    def test_set_remodel_parameters(self):
        remodel_file = os.path.realpath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data/simple_reorder_rmdl.json",
            )
        )
        with open(remodel_file) as fp:
            json_obj = json.load(fp)
        params = {"remodel_string": json.dumps(json_obj)}
        arguments = {}
        ProcessServices.set_remodel_parameters(arguments, params)
        self.assertTrue(arguments)
        self.assertIn("remodel_operations", arguments)
        self.assertEqual(len(arguments["remodel_operations"]), 2)

        params = {}
        arguments = {}
        ProcessServices.set_remodel_parameters(arguments, params)
        self.assertFalse(arguments)
        self.assertNotIn("remodel_operations", arguments)

    def test_get_service_info(self):
        params = {
            bc.SERVICE: "schema_validate",
            bc.EXPAND_DEFS: True,
            bc.CHECK_FOR_WARNINGS: False,
            bc.INCLUDE_DESCRIPTION_TAGS: True,
        }

        expected_result = {
            bc.SERVICE: "schema_validate",
            bc.COMMAND: "validate",
            bc.COMMAND_TARGET: "schema",
            bc.HAS_COLUMN_NAMES: True,
            bc.CHECK_FOR_WARNINGS: False,
            bc.EXPAND_DEFS: True,
            bc.INCLUDE_DESCRIPTION_TAGS: True,
            bc.INCLUDE_PRERELEASES: False,
            bc.REQUEST_TYPE: bc.FROM_SERVICE,
        }

        result = ProcessServices.get_service_info(params)
        self.assertEqual(result, expected_result)

        params = {bc.SERVICE: "get_services"}

        expected_result = {
            bc.SERVICE: "get_services",
            bc.COMMAND: "get_services",
            bc.COMMAND_TARGET: "",
            bc.HAS_COLUMN_NAMES: True,
            bc.CHECK_FOR_WARNINGS: True,
            bc.EXPAND_DEFS: False,
            bc.INCLUDE_DESCRIPTION_TAGS: True,
            bc.INCLUDE_PRERELEASES: False,
            bc.REQUEST_TYPE: bc.FROM_SERVICE,
        }

        result = ProcessServices.get_service_info(params)
        self.assertEqual(result, expected_result)

    def test_set_input_schema(self):
        from hed.schema import HedSchema, load_schema_version

        schema = load_schema_version("8.2.0")
        schema_as_string = schema.get_as_xml_string()

        parameters = {bc.SCHEMA_STRING: schema_as_string}
        result = ProcessServices.get_input_schema(parameters)
        self.assertIsInstance(result, HedSchema)

        parameters = {
            bc.SCHEMA_URL: "https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml"
        }
        result = ProcessServices.get_input_schema(parameters)
        self.assertIsInstance(result, HedSchema)

        parameters = {bc.SCHEMA_VERSION: "8.2.0"}
        result = ProcessServices.get_input_schema(parameters)
        self.assertIsInstance(result, HedSchema)

        parameters = {bc.SCHEMA_STRING: "invalid_schema_string"}
        with self.assertRaises(HedFileError):
            ProcessServices.get_input_schema(parameters)

    def test_get_services_list(self):
        with self.app.app_context():
            results = ProcessServices.get_services_list()
            self.assertIsInstance(results, dict, "services_list returns a dictionary")
            self.assertTrue(
                results["data"],
                "services_list return dictionary has a data key with non empty value",
            )

    def test_process_services_sidecar(self):
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/both_types_events_errors.json",
        )
        with open(json_path) as f:
            data = json.load(f)
        json_text = json.dumps(data)
        fb = io.StringIO(json_text)
        arguments = {
            bc.SERVICE: "sidecar_validate",
            bc.SCHEMA: load_schema_version("8.2.0"),
            bc.COMMAND: "validate",
            bc.COMMAND_TARGET: "sidecar",
            bc.SIDECAR: Sidecar(files=fb, name="JSON_Sidecar"),
        }
        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(
                response["error_type"],
                "sidecar_validation services should not have a fatal error when file is invalid",
            )
            results = response["results"]
            self.assertEqual(
                "warning",
                results["msg_category"],
                "sidecar_validation services has success on bids_events.json",
            )
            self.assertEqual(
                json.dumps("8.2.0"),
                results[bc.SCHEMA_VERSION],
                "Version 8.2.0 was used",
            )

    def test_process_services_sidecar_a(self):
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json"
        )
        with open(json_path) as f:
            data = json.load(f)
        json_text = json.dumps(data)
        fb = io.StringIO(json_text)
        hed_schema = load_schema_version("8.2.0")
        json_sidecar = Sidecar(files=fb, name="JSON_Sidecar")
        arguments = {
            bc.SERVICE: "sidecar_validate",
            bc.SCHEMA: hed_schema,
            bc.COMMAND: "validate",
            bc.COMMAND_TARGET: "sidecar",
            bc.SIDECAR: json_sidecar,
        }
        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(
                response["error_type"],
                "sidecar_validation services should not have a fatal error when file is invalid",
            )
            results = response["results"]
            self.assertEqual(
                "success",
                results["msg_category"],
                "sidecar_validation services has success on bids_events.json",
            )
            self.assertEqual(
                json.dumps("8.2.0"),
                results[bc.SCHEMA_VERSION],
                "Version 8.2.0 was used",
            )

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json"
        )
        with open(json_path) as f:
            data = json.load(f)
        json_text = json.dumps(data)
        fb = io.StringIO(json_text)
        arguments[bc.SIDECAR] = Sidecar(files=fb, name="JSON_Sidecar_BAD")
        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(
                response["error_type"],
                "sidecar_validation services should not have a error when file is valid",
            )
            results = response["results"]
            self.assertTrue(
                results["data"],
                "sidecar_validation produces errors when file not valid",
            )
            self.assertEqual(
                "warning",
                results["msg_category"],
                "sidecar_validation did not valid with 8.2.0",
            )
            self.assertEqual(
                json.dumps("8.2.0"), results["schema_version"], "Version 8.2.0 was used"
            )


if __name__ == "__main__":
    unittest.main()
