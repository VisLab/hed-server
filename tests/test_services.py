"""
Comprehensive test coverage for ProcessServices class.

ProcessServices handles REST API request processing by:
- Extracting and parsing JSON service requests
- Loading HED schemas from various sources (version, URL, string)
- Setting up input objects (events, sidecars, spreadsheets, strings)
- Configuring parameters for domain-specific operations
- Routing requests to appropriate operation handlers (events, sidecars, spreadsheets, strings, schemas)
- Packaging results in standardized format

Test Organization:
- REQUEST PROCESSING: set_input_from_request and related parameter extraction
- SCHEMA LOADING: get_input_schema for various schema sources
- SIDECAR HANDLING: set_sidecar and multi-file sidecar merging
- INPUT OBJECTS: set_input_objects for events, spreadsheets, and HED strings
- DEFINITIONS: set_definitions and get_definitions with validation
- QUERIES: set_queries for search operations
- REMODEL OPERATIONS: set_remodel_parameters for event remodeling
- SERVICE ROUTING: get_process, process for different operation targets
- RESULT PACKAGING: package_spreadsheet for output transformation
- UTILITY FUNCTIONS: normalize_boolean, get_list, get_parameter_string
- SERVICES METADATA: get_services_list for service documentation

Test Approach:
- Uses real Flask app context and werkzeug test utilities
- No mocking of hedtools classes (Sidecar, HedString, etc.)
- Tests with real data files from tests/data/
- Validates error handling and edge cases
"""

import io
import json
import os
import unittest

from hed.errors.exceptions import HedFileError
from hed.models import Sidecar, TabularInput
from hed.schema import HedSchema, load_schema_version
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from hedweb.constants import base_constants as bc
from hedweb.process_service import ProcessServices
from tests.test_web_base import TestWebBase


class TestProcessServices(TestWebBase):
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
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
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
            self.assertIsInstance(arguments[bc.SIDECAR], Sidecar, "should contain a sidecar")
            self.assertIsInstance(arguments[bc.SCHEMA], HedSchema, "should have a HED schema")
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
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
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
            self.assertIsInstance(arguments[bc.SIDECAR], Sidecar, "should contain a sidecar")
            self.assertIsInstance(arguments[bc.SCHEMA], HedSchema, "should have a HED schema")
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
        path_upper = "data/eeg_ds003654s_hed_inheritance/task-FacePerception_events.json"
        path_lower2 = "data/eeg_ds003654s_hed_inheritance/sub-002/sub-002_task-FacePerception_events.json"
        path_lower3 = "data/eeg_ds003654s_hed_inheritance/sub-003/sub-003_task-FacePerception_events.json"
        sidecar_path_upper = os.path.join(os.path.dirname(os.path.realpath(__file__)), path_upper)
        sidecar_path_lower2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), path_lower2)
        sidecar_path_lower3 = os.path.join(os.path.dirname(os.path.realpath(__file__)), path_lower3)

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
        self.assertIn("event_type", sidecar2.loaded_dict, "merged sidecar should have event_type")

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
        self.assertIn("event_type", sidecar3.loaded_dict, "merged sidecar should have event_type")

    def test_set_input_objects(self):
        sidecar_path = "data/task-FacePerception_events.json"
        sidecar_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), sidecar_path)

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
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
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

        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
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
            self.assertEqual(json.dumps("8.2.0"), results["schema_version"], "Version 8.2.0 was used")

    def test_normalize_boolean(self):
        from hedweb.process_service import normalize_boolean

        # None → default
        self.assertFalse(normalize_boolean(None))
        self.assertTrue(normalize_boolean(None, default=True))

        # Actual booleans pass through unchanged
        self.assertTrue(normalize_boolean(True))
        self.assertFalse(normalize_boolean(False))

        # Truthy strings
        for truthy in ("true", "True", "TRUE", "on", "ON", "1", "yes", "YES"):
            self.assertTrue(normalize_boolean(truthy), f"'{truthy}' should normalize to True")

        # Falsy strings
        for falsy in ("false", "off", "0", "no", "", "random"):
            self.assertFalse(normalize_boolean(falsy), f"'{falsy}' should normalize to False")

        # Integers
        self.assertTrue(normalize_boolean(1))
        self.assertTrue(normalize_boolean(42))
        self.assertFalse(normalize_boolean(0))

        # Other types → default
        self.assertFalse(normalize_boolean([]))
        self.assertFalse(normalize_boolean({}))

    def test_set_definitions(self):
        from hed.schema import load_schema_version

        from hedweb.process_service import ProcessServices

        schema = load_schema_version("8.2.0")
        def_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/def_test.json")
        with open(def_path) as f:
            def_string = f.read()

        # With a valid definition string
        arguments = {bc.SCHEMA: schema}
        params = {bc.DEFINITION_STRING: def_string}
        ProcessServices.set_definitions(arguments, params)
        self.assertIn(bc.DEFINITIONS, arguments)

        # With no definition string — should still populate DEFINITIONS key (empty)
        arguments2 = {bc.SCHEMA: schema}
        params2 = {}
        ProcessServices.set_definitions(arguments2, params2)
        self.assertIn(bc.DEFINITIONS, arguments2)
        self.assertIsNone(arguments2[bc.DEFINITIONS])

    def test_set_queries(self):
        from hedweb.process_service import ProcessServices

        # With queries present
        arguments = {}
        params = {bc.QUERIES: ["Event", "Sensory-event"], bc.QUERY_NAMES: ["q1", "q2"]}
        ProcessServices.set_queries(arguments, params)
        self.assertIn(bc.QUERIES, arguments)
        self.assertEqual(arguments[bc.QUERIES], ["Event", "Sensory-event"])
        self.assertEqual(arguments[bc.QUERY_NAMES], ["q1", "q2"])

        # With no queries key — should not set anything
        arguments2 = {}
        ProcessServices.set_queries(arguments2, {})
        self.assertNotIn(bc.QUERIES, arguments2)
        self.assertNotIn(bc.QUERY_NAMES, arguments2)

        # With empty queries list — should not set
        arguments3 = {}
        ProcessServices.set_queries(arguments3, {bc.QUERIES: []})
        self.assertNotIn(bc.QUERIES, arguments3)

    def test_get_definitions_valid(self):
        """Test get_definitions with valid JSON string containing definitions."""
        from hedweb.process_service import ProcessServices

        schema = load_schema_version("8.2.0")
        def_string = '{"definitions": ["(Definition/TestDef/#, (Age/#))", "(Definition/Color, (Red))"]}'
        result = ProcessServices.get_definitions(def_string, schema)
        self.assertIsNotNone(result, "should return DefinitionDict for valid definitions")

    def test_get_definitions_empty_string(self):
        """Test get_definitions with empty string returns None."""
        from hedweb.process_service import ProcessServices

        schema = load_schema_version("8.2.0")
        result = ProcessServices.get_definitions("", schema)
        self.assertIsNone(result, "should return None for empty string")

    def test_get_definitions_single_def_string(self):
        """Test get_definitions with a single definition as string."""
        from hedweb.process_service import ProcessServices

        schema = load_schema_version("8.2.0")
        def_string = '{"definitions": "(Definition/TestDef/#, (Age/#))"}'
        result = ProcessServices.get_definitions(def_string, schema)
        self.assertIsNotNone(result, "should return DefinitionDict for single definition string")

    def test_get_definitions_invalid_json(self):
        """Test get_definitions with invalid JSON raises HedFileError."""
        from hedweb.process_service import ProcessServices

        schema = load_schema_version("8.2.0")
        def_string = '{"definitions": invalid json}'
        with self.assertRaises(HedFileError) as context:
            ProcessServices.get_definitions(def_string, schema)
        self.assertIn("valid JSON", str(context.exception))

    def test_get_definitions_non_dict(self):
        """Test get_definitions with non-dict JSON raises HedFileError."""
        from hedweb.process_service import ProcessServices

        schema = load_schema_version("8.2.0")
        def_string = '["Definition/TestDef", "Definition/Color"]'
        with self.assertRaises(HedFileError) as context:
            ProcessServices.get_definitions(def_string, schema)
        self.assertIn("object", str(context.exception))

    def test_get_definitions_missing_key(self):
        """Test get_definitions with missing 'definitions' key returns None."""
        from hedweb.process_service import ProcessServices

        schema = load_schema_version("8.2.0")
        def_string = '{"something_else": "value"}'
        result = ProcessServices.get_definitions(def_string, schema)
        self.assertIsNone(result, "should return None when 'definitions' key is missing")

    def test_get_definitions_null_definitions(self):
        """Test get_definitions with null 'definitions' key returns None."""
        from hedweb.process_service import ProcessServices

        schema = load_schema_version("8.2.0")
        def_string = '{"definitions": null}'
        result = ProcessServices.get_definitions(def_string, schema)
        self.assertIsNone(result, "should return None when 'definitions' is null")

    # ========== ADDITIONAL COMPREHENSIVE COVERAGE TESTS ==========
    def test_get_list_with_string(self):
        """Test get_list converts string to single-element list."""
        result = ProcessServices.get_list("test_key", {"test_key": "single_value"})
        self.assertEqual(result, ["single_value"])

    def test_get_list_with_list(self):
        """Test get_list returns list as-is."""
        result = ProcessServices.get_list("test_key", {"test_key": ["a", "b", "c"]})
        self.assertEqual(result, ["a", "b", "c"])

    def test_get_list_missing_key(self):
        """Test get_list returns empty list for missing key."""
        result = ProcessServices.get_list("missing_key", {})
        self.assertEqual(result, [])

    def test_get_list_none_value(self):
        """Test get_list returns empty list for None value."""
        result = ProcessServices.get_list("test_key", {"test_key": None})
        self.assertEqual(result, [])

    def test_get_list_empty_list(self):
        """Test get_list returns empty list for empty list."""
        result = ProcessServices.get_list("test_key", {"test_key": []})
        self.assertEqual(result, [])

    def test_get_process_events(self):
        """Test get_process returns EventOperations for 'events' target."""
        from hedweb.event_operations import EventOperations

        result = ProcessServices.get_process("events")
        self.assertIsInstance(result, EventOperations)

    def test_get_process_sidecar(self):
        """Test get_process returns SidecarOperations for 'sidecar' target."""
        from hedweb.sidecar_operations import SidecarOperations

        result = ProcessServices.get_process("sidecar")
        self.assertIsInstance(result, SidecarOperations)

    def test_get_process_spreadsheet(self):
        """Test get_process returns SpreadsheetOperations for 'spreadsheet' target."""
        from hedweb.spreadsheet_operations import SpreadsheetOperations

        result = ProcessServices.get_process("spreadsheet")
        self.assertIsInstance(result, SpreadsheetOperations)

    def test_get_process_strings(self):
        """Test get_process returns StringOperations for 'strings' target."""
        from hedweb.string_operations import StringOperations

        result = ProcessServices.get_process("strings")
        self.assertIsInstance(result, StringOperations)

    def test_get_process_schemas(self):
        """Test get_process returns SchemaOperations for 'schemas' target."""
        from hedweb.schema_operations import SchemaOperations

        result = ProcessServices.get_process("schemas")
        self.assertIsInstance(result, SchemaOperations)

    def test_get_process_invalid_target(self):
        """Test get_process raises HedFileError for invalid target."""
        with self.assertRaises(HedFileError) as context:
            ProcessServices.get_process("invalid_target")
        self.assertIn("invalid", str(context.exception).lower())

    def test_package_spreadsheet_with_success(self):
        """Test package_spreadsheet converts SpreadsheetInput to CSV string on success."""
        from hed import SpreadsheetInput

        # Create a sample spreadsheet
        tsv_data = "col1\tcol2\tcol3\n1\t2\t(Event)\n3\t4\t(Age)"
        spreadsheet = SpreadsheetInput(
            file=io.StringIO(tsv_data), file_type=".tsv", tag_columns=[3], has_column_names=True, name="test.tsv"
        )

        results = {"msg_category": "success", bc.SPREADSHEET: spreadsheet, "data": "some data"}

        packaged = ProcessServices.package_spreadsheet(results)
        self.assertIn(bc.SPREADSHEET, packaged)
        self.assertIsInstance(packaged[bc.SPREADSHEET], str)
        self.assertIn("col1", packaged[bc.SPREADSHEET])

    def test_package_spreadsheet_with_warning(self):
        """Test package_spreadsheet deletes spreadsheet on non-success."""
        from hed import SpreadsheetInput

        tsv_data = "col1\tcol2\tcol3\n1\t2\t(Event)"
        spreadsheet = SpreadsheetInput(
            file=io.StringIO(tsv_data), file_type=".tsv", tag_columns=[3], has_column_names=True, name="test.tsv"
        )

        results = {
            "msg_category": "warning",
            bc.SPREADSHEET: spreadsheet,
        }

        packaged = ProcessServices.package_spreadsheet(results)
        self.assertNotIn(bc.SPREADSHEET, packaged)

    def test_package_spreadsheet_no_spreadsheet(self):
        """Test package_spreadsheet handles missing spreadsheet gracefully."""
        results = {"msg_category": "success", "data": "some data"}

        packaged = ProcessServices.package_spreadsheet(results)
        self.assertEqual(packaged, results)

    def test_get_parameter_string_empty_params(self):
        """Test get_parameter_string with empty parameters."""
        result = ProcessServices.get_parameter_string(None)
        self.assertEqual(result, "\tParameters: []")

    def test_get_parameter_string_single_params(self):
        """Test get_parameter_string with single string parameters."""
        params = ["param1", "param2", "param3"]
        result = ProcessServices.get_parameter_string(params)
        self.assertIn("param1", result)
        self.assertIn("param2", result)
        self.assertIn("param3", result)

    def test_get_parameter_string_list_params(self):
        """Test get_parameter_string with 'or' alternatives in lists."""
        params = ["param1", ["param2a", "param2b"], "param3"]
        result = ProcessServices.get_parameter_string(params)
        self.assertIn("param1", result)
        self.assertIn("param2a or param2b", result)
        self.assertIn("param3", result)

    def test_process_events_target(self):
        """Test process method with events operation target."""
        events_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/sub-002_task-FacePerception_run-1_events.tsv",
        )
        with open(events_path) as fp:
            events_data = fp.read()

        sidecar_path = "data/task-FacePerception_events.json"
        sidecar_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), sidecar_path)
        sidecar = Sidecar(sidecar_path)

        arguments = {
            bc.SERVICE: "events_validate",
            bc.COMMAND: "validate",
            bc.COMMAND_TARGET: "events",
            bc.SCHEMA: load_schema_version("8.2.0"),
            bc.EVENTS: TabularInput(file=io.StringIO(events_data), sidecar=sidecar, name="Events"),
            bc.CHECK_FOR_WARNINGS: True,
        }

        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(response["error_type"])
            self.assertEqual(response[bc.SERVICE], "events_validate")

    def test_process_strings_target(self):
        """Test process method with strings operation target."""
        from hed import HedString

        schema = load_schema_version("8.2.0")
        arguments = {
            bc.SERVICE: "strings_validate",
            bc.COMMAND: "validate",
            bc.COMMAND_TARGET: "strings",
            bc.SCHEMA: schema,
            bc.STRING_LIST: [
                HedString("(Event, (Age))", hed_schema=schema),
                HedString("(Sensory-event)", hed_schema=schema),
            ],
            bc.CHECK_FOR_WARNINGS: True,
        }

        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(response["error_type"])
            self.assertEqual(response[bc.SERVICE], "strings_validate")

    def test_process_invalid_target_missing(self):
        """Test process with invalid/missing command target."""
        arguments = {
            bc.SERVICE: "invalid_validate",
            bc.COMMAND: "validate",
            bc.COMMAND_TARGET: "invalid",
        }

        with self.app.app_context():
            with self.assertRaises(HedFileError):
                ProcessServices.process(arguments)

    def test_process_get_services(self):
        """Test process method with get_services command."""
        arguments = {
            bc.SERVICE: "get_services",
            bc.COMMAND: "get_services",
        }

        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(response["error_type"])
            self.assertIn("data", response["results"])

    def test_set_parameters_all_options(self):
        """Test set_parameters with all option flags."""
        arguments = {}
        params = {
            bc.COLUMNS_CATEGORICAL: ["col1"],
            bc.COLUMNS_VALUE: ["col2"],
            bc.COLUMNS_SKIP: ["col3"],
            bc.TAG_COLUMNS: ["col4"],
            bc.INCLUDE_CONTEXT: True,
            bc.REMOVE_TYPES: True,
            bc.REPLACE_DEFS: True,
            bc.EXPAND_DEFS: True,
            bc.INCLUDE_DESCRIPTION_TAGS: True,
            bc.INCLUDE_SUMMARIES: True,
        }
        ProcessServices.set_parameters(arguments, params)

        self.assertEqual(arguments[bc.COLUMNS_CATEGORICAL], ["col1"])
        self.assertEqual(arguments[bc.COLUMNS_VALUE], ["col2"])
        self.assertEqual(arguments[bc.COLUMNS_SKIP], ["col3"])
        self.assertTrue(arguments[bc.INCLUDE_CONTEXT])
        self.assertTrue(arguments[bc.REMOVE_TYPES])
        self.assertTrue(arguments[bc.REPLACE_DEFS])
        self.assertTrue(arguments[bc.EXPAND_DEFS])


if __name__ == "__main__":
    unittest.main()
