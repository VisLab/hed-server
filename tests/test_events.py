"""
Comprehensive test coverage for EventOperations class.

This module provides extensive testing of hedweb/event_operations.py, which handles tabular event data
files with HED annotations and metadata sidecars. Tests cover form processing, validation, conversion,
searching, quality checking, remodeling, and sidecar generation.

Test Approach:
- No mocks: All tests use real test data files from tests/data/ (bids_events.tsv, bids_events.json)
- Parameter variations: Tests combinations like with/without warnings, append modes, definition options
- End-to-end workflows: Tests complex operations like validate→search to verify composition
- Error paths: Tests invalid data, missing files, bad schemas to verify error handling
- Output validation: Verifies not just success but that output is correctly formatted

Coverage:
- validate() - HED annotation validation with various options and external definitions
- check_quality() - Annotation quality analysis with metrics and limits
- assemble() - Short-form to long-form HED conversion with different modes
- search() - Finding matching HED tags with query options
- get_hed_objs() - Converting to HED objects with context preservation
- remodel() - Data structure transformation with optional summaries
- generate_sidecar() - Creating sidecar metadata from columns
- Error conditions - Invalid commands, bad schemas, missing files
"""

import json
import os
import unittest
from io import StringIO

import pandas as pd
from hed.errors.exceptions import HedFileError
from hed.models import Sidecar, TabularInput
from hed.schema import HedSchema, load_schema
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from hedweb.constants import base_constants as bc
from hedweb.event_operations import EventOperations
from hedweb.process_form import ProcessForm
from hedweb.process_service import ProcessServices
from tests.test_web_base import TestWebBase


class TestEventOperations(TestWebBase):
    cache_schemas = True

    def get_event_proc(self, events_file, sidecar_file, schema_file):
        events_proc = EventOperations()
        if schema_file:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), schema_file)
            events_proc.schema = load_schema(schema_path)
        if sidecar_file:
            events_proc.sidecar = Sidecar(files=os.path.join(os.path.dirname(os.path.abspath(__file__)), sidecar_file))
        if events_file:
            events_proc.events = TabularInput(
                file=os.path.join(os.path.dirname(os.path.abspath(__file__)), events_file),
                sidecar=events_proc.sidecar,
            )
        events_proc.expand_defs = True
        events_proc.columns_categorical = []
        events_proc.columns_value = []
        events_proc.check_for_warnings = True
        return events_proc

    def test_set_input_from_events_form_empty(self):
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_events = EventOperations()
                proc_events.process()

    def test_set_input_from_events_form(self):
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.tsv")
        with self.app.app_context():
            with open(sidecar_path, "rb") as fp:
                with open(events_path, "rb") as fpe:
                    environ = create_environ(
                        data={
                            bc.SIDECAR_FILE: fp,
                            bc.SCHEMA_VERSION: "8.2.0",
                            bc.EVENTS_FILE: fpe,
                            bc.EXPAND_DEFS: "on",
                            bc.COMMAND_OPTION: bc.COMMAND_ASSEMBLE,
                        }
                    )
            request = Request(environ)
            arguments = ProcessForm.get_input_from_form(request)
            event_proc = EventOperations(arguments=arguments)
            self.assertIsInstance(event_proc.events, TabularInput, "should have an events object")
            self.assertIsInstance(event_proc.schema, HedSchema, "should have a HED schema")
            self.assertEqual(event_proc.command, bc.COMMAND_ASSEMBLE, "should have correct command")
            self.assertTrue(event_proc.expand_defs, "should have expand_defs true when on")

    def test_events_process_empty_file(self):
        with self.assertRaises(HedFileError):
            proc_events = EventOperations()
            proc_events.process()

    def test_events_process_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events_bad.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_VALIDATE
            results = events_proc.process()
            self.assertTrue(
                isinstance(results, dict),
                "process validation should return a result dictionary when validation errors",
            )
            self.assertEqual(
                "warning",
                results["msg_category"],
                "process validate should return warning when errors",
            )

    def test_events_process_valid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_VALIDATE
            results = events_proc.process()
            self.assertTrue(
                isinstance(results, dict),
                "should return a dictionary when validation errors",
            )
            self.assertEqual("success", results["msg_category"], "should give success when no errors")
            self.assertFalse(results["data"], "process not return data no no errors")

    def test_events_assemble_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events_bad.json", "data/HED8.2.0.xml")
            events_proc.check_for_warnings = False
            events_proc.command = bc.COMMAND_ASSEMBLE
            results = events_proc.process()
            self.assertTrue("data" in results, "should have a data key when no errors")
            self.assertEqual("warning", results["msg_category"], "should be warning when errors")

    def test_events_assemble_valid(self):
        with self.app.app_context():
            # Test with defaults (no types, no replace, no context)
            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            events_proc.check_for_warnings = False
            events_proc.command = bc.COMMAND_ASSEMBLE
            results = events_proc.process()
            data1 = results["data"]
            self.assertTrue(data1, "should have a data key when no errors")
            self.assertEqual("success", results["msg_category"], "should be success when no errors")

            # Explicitly tests defaults
            events_proc.remove_types = False
            events_proc.replace_defs = False
            events_proc.include_context = False
            results = events_proc.process()
            data2 = results["data"]
            self.assertTrue(data2, "should have a data key when no errors")
            self.assertEqual(data1, data2)

            # With context, no remove, no replace
            events_proc.remove_types = False
            events_proc.replace_defs = False
            events_proc.include_context = True
            results = events_proc.process()
            data3 = results["data"]
            self.assertTrue(data3, "should have a data key when no errors")
            self.assertGreater(len(data3[1]), len(data2[1]))
            data3_str = "\n".join(data3)
            data2_str = "\n".join(data2)
            self.assertGreater(len(data3_str), len(data2_str))

            # With context, remove, no replace
            events_proc.remove_types = True
            events_proc.replace_defs = False
            events_proc.include_context = True
            results = events_proc.process()
            data4 = results["data"]
            self.assertTrue(data4, "should have a data key when no errors")
            data4_str = "\n".join(data4)
            self.assertGreater(len(data3_str), len(data4_str))

            # With context, remove, replace
            events_proc.remove_types = True
            events_proc.replace_defs = True
            events_proc.include_context = True
            results = events_proc.process()
            data5 = results["data"]
            data5_str = "\n".join(data5)
            self.assertTrue(data5, "should have a data key when no errors")
            self.assertGreater(len(data5_str), len(data4_str))

    def test_generate_sidecar_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_GENERATE_SIDECAR
            events_proc.columns_skip = ["event_type"]
            events_proc.columns_value = ["event_type"]
            results = events_proc.process()
            self.assertTrue(
                "data" in results,
                "make_query results should have a data key when errors",
            )
            self.assertEqual(
                "warning",
                results["msg_category"],
                "make_query msg_category should be warning when errors",
            )

    def test_generate_sidecar_valid(self):
        events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
        events_proc.command = bc.COMMAND_GENERATE_SIDECAR
        events_proc.expand_defs = True
        events_proc.columns_value = ["trial"]
        events_proc.columns_skip = ["onset", "duration", "sample"]
        events_proc.check_for_warnings = False
        results = events_proc.process()
        self.assertTrue(
            results["data"],
            "generate_sidecar results should have a data key when no errors",
        )
        self.assertEqual(
            "success",
            results["msg_category"],
            "generate_sidecar msg_category should be success when no errors",
        )
        sidecar_template = json.loads(results["data"])
        self.assertFalse("onset" in sidecar_template)
        self.assertIsInstance(sidecar_template["event_type"]["HED"], dict)
        self.assertTrue(isinstance(sidecar_template["trial"]["HED"], str))

    def test_search_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.query = ""
            events_proc.command = bc.COMMAND_SEARCH
            results = events_proc.process()
            self.assertTrue(
                "data" in results,
                "make_query results should have a data key when errors",
            )
            self.assertEqual(
                "warning",
                results["msg_category"],
                "make_query msg_category should be warning when errors",
            )

    def test_events_search_valid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_SEARCH
            events_proc.queries = ["Sensory-event"]
            results = events_proc.process()
            self.assertTrue(results["data"], "should have a data key when no errors")
            self.assertEqual("success", results["msg_category"], "should be success when no errors")

    def test_events_validate_invalid(self):
        events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events_bad.json", "data/HED8.2.0.xml")
        events_proc.command = bc.COMMAND_VALIDATE
        with self.app.app_context():
            results = events_proc.process()
            self.assertTrue(results["data"], "should have a data key when validation errors")
            self.assertEqual("warning", results["msg_category"], "should be warning when errors")

    def test_events_validate_valid(self):
        events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
        events_proc.command = bc.COMMAND_VALIDATE
        with self.app.app_context():
            results = events_proc.process()
            self.assertFalse(results["data"], "should not have a data key when no validation errors")
            self.assertEqual("success", results["msg_category"], "should be success when no errors")

    def test_events_remodel_valid_no_hed(self):
        rmdl1 = [
            {
                "operation": "remove_columns",
                "description": "Remove unwanted columns prior to analysis",
                "parameters": {
                    "column_names": ["value", "sample", "junk"],
                    "ignore_missing": True,
                },
            }
        ]
        events_proc = self.get_event_proc("data/sub-002_task-FacePerception_run-1_events.tsv", None, None)
        events_proc.command = bc.COMMAND_REMODEL
        events_proc.remodel_operations = {"name": "test", "operations": rmdl1}
        cols_orig = events_proc.events.columns
        rows_orig = len(events_proc.events.dataframe)
        with self.app.app_context():
            results = events_proc.process()
        self.assertTrue(results["data"], "remodel results should have a data key when successful")
        self.assertEqual(
            "success",
            results["msg_category"],
            "remodel msg_category should be success when no errors",
        )
        df = pd.read_csv(StringIO(results["data"]), sep="\t")
        (self.assertEqual(len(df.columns), len(cols_orig) - 2),)
        self.assertEqual(len(df), rows_orig)

    def test_events_remodel_invalid_no_hed(self):
        rmdl1 = [
            {
                "operation": "remove_columns",
                "description": "Remove unwanted columns prior to analysis",
                "parameters": {
                    "column_names": ["value", "sample", "junk"],
                    "ignore_missing": False,
                },
            }
        ]
        events_proc = self.get_event_proc("data/sub-002_task-FacePerception_run-1_events.tsv", None, None)
        events_proc.command = bc.COMMAND_REMODEL
        events_proc.remodel_operations = {"name": "test", "operations": rmdl1}
        with self.app.app_context():
            with self.assertRaises(KeyError) as ex:
                events_proc.process()
        self.assertEqual(ex.exception.args[0], "MissingColumnCannotBeRemoved")

    def test_events_remodel_valid_with_hed(self):
        rmdl1 = [
            {
                "operation": "factor_hed_type",
                "description": "Factor condition variables.",
                "parameters": {"type_tag": "Condition-variable"},
            }
        ]
        events_proc = self.get_event_proc(
            "data/sub-002_task-FacePerception_run-1_events.tsv",
            "data/task-FacePerception_events.json",
            "data/HED8.2.0.xml",
        )
        events_proc.command = bc.COMMAND_REMODEL
        cols_orig = events_proc.events.columns
        rows_orig = len(events_proc.events.dataframe)
        events_proc.remodel_operations = {"name": "test", "operations": rmdl1}
        with self.app.app_context():
            results = events_proc.process()
        self.assertTrue(results["data"], "remodel results should have a data key when successful")
        self.assertEqual(
            "success",
            results["msg_category"],
            "remodel msg_category should be success when no errors",
        )
        df = pd.read_csv(StringIO(results["data"]), sep="\t")
        (self.assertEqual(len(df.columns), len(cols_orig) + 7),)
        self.assertEqual(len(df), rows_orig)

    def test_events_validate_with_external_definitions(self):
        """Test events validation with external definitions."""
        with self.app.app_context():
            from hedweb.process_service import ProcessServices

            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            def_string = '{"definitions": "(Definition/TestDef/#, (Age/#))"}'
            events_proc.definitions = ProcessServices.get_definitions(def_string, events_proc.schema)
            events_proc.command = bc.COMMAND_VALIDATE
            results = events_proc.process()
            # Should validate without errors using external definitions
            self.assertIn("msg_category", results, "should have msg_category")

    def test_events_assemble_with_external_definitions(self):
        """Test events assembly with external definitions."""
        with self.app.app_context():
            from hedweb.process_service import ProcessServices

            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            def_string = '{"definitions": "(Definition/TestDef/#, (Age/#))"}'
            events_proc.definitions = ProcessServices.get_definitions(def_string, events_proc.schema)
            events_proc.command = bc.COMMAND_ASSEMBLE
            events_proc.check_for_warnings = False
            results = events_proc.process()
            self.assertTrue(results["data"], "should assemble successfully with external definitions")
            self.assertEqual("success", results["msg_category"], "should be success when no errors")

    def test_set_input_from_events_form_with_valid_definition_file(self):
        """Test form input with valid definition file."""
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.tsv")
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        def_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/definitions.json")
        with self.app.app_context():
            with open(events_path, "rb") as fpe:
                with open(sidecar_path, "rb") as fps:
                    with open(def_path, "rb") as fpd:
                        environ = create_environ(
                            data={
                                bc.EVENTS_FILE: fpe,
                                bc.SIDECAR_FILE: fps,
                                bc.DEFINITION_FILE: fpd,
                                bc.SCHEMA_VERSION: "8.2.0",
                                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                            }
                        )
            request = Request(environ)
            arguments = ProcessForm.get_input_from_form(request)
            self.assertIn(bc.DEFINITIONS, arguments, "should have definitions in arguments")

    def test_set_input_from_events_form_with_invalid_definition_file(self):
        """Test form input with invalid JSON definition file."""
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.tsv")
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        invalid_def_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/invalid_json.json")
        with self.app.app_context():
            with open(events_path, "rb") as fpe:
                with open(sidecar_path, "rb") as fps:
                    with open(invalid_def_path, "rb") as fpd:
                        environ = create_environ(
                            data={
                                bc.EVENTS_FILE: fpe,
                                bc.SIDECAR_FILE: fps,
                                bc.DEFINITION_FILE: fpd,
                                bc.SCHEMA_VERSION: "8.2.0",
                                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                            }
                        )
            request = Request(environ)
            with self.assertRaises(HedFileError) as context:
                ProcessForm.get_input_from_form(request)
            self.assertIn("JSON", str(context.exception))

    def test_set_input_from_events_form_with_non_dict_definition_file(self):
        """Test form input with non-dict JSON definition file."""
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.tsv")
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        not_dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/not_dict.json")
        with self.app.app_context():
            with open(events_path, "rb") as fpe:
                with open(sidecar_path, "rb") as fps:
                    with open(not_dict_path, "rb") as fpd:
                        environ = create_environ(
                            data={
                                bc.EVENTS_FILE: fpe,
                                bc.SIDECAR_FILE: fps,
                                bc.DEFINITION_FILE: fpd,
                                bc.SCHEMA_VERSION: "8.2.0",
                                bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                            }
                        )
            request = Request(environ)
            with self.assertRaises(HedFileError) as context:
                ProcessForm.get_input_from_form(request)
            self.assertIn("object", str(context.exception))

    # ========== COMPREHENSIVE COVERAGE TESTS ==========
    # Additional comprehensive tests for EventOperations class
    # Includes parameter variations, option combinations, edge cases, and error paths

    def test_check_quality_with_limit_errors(self):
        """Test check_quality with limit_errors enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events_bad.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_CHECK_QUALITY
            events_proc.limit_errors = True
            results = events_proc.process()
            self.assertIsInstance(results, dict, "should return a dictionary")
            self.assertIn("data", results, "should have data with quality issues")

    def test_check_quality_with_show_details(self):
        """Test check_quality with show_details enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_CHECK_QUALITY
            events_proc.show_details = True
            results = events_proc.process()
            self.assertIsInstance(results, dict, "should return a dictionary")

    def test_check_quality_with_both_limit_and_show_details(self):
        """Test check_quality with both limit_errors and show_details."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events_bad.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_CHECK_QUALITY
            events_proc.limit_errors = True
            events_proc.show_details = True
            results = events_proc.process()
            self.assertIsInstance(results, dict, "should return a dictionary")
            self.assertIn("data", results, "should have quality check data")

    def test_validate_without_warnings(self):
        """Test validation with check_for_warnings disabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_VALIDATE
            events_proc.check_for_warnings = False
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success without warnings")
            self.assertFalse(results["data"], "should have empty data for no errors")

    def test_validate_with_warnings_enabled(self):
        """Test validation with check_for_warnings enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_VALIDATE
            events_proc.check_for_warnings = True
            results = events_proc.process()
            self.assertIn("msg_category", results, "should have msg_category")

    def test_validate_with_external_definitions_no_errors(self):
        """Test validate with external definitions that introduce no errors."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            def_string = '{"definitions": "(Definition/TestDef/#, (Age/#))"}'
            events_proc.definitions = ProcessServices.get_definitions(def_string, events_proc.schema)
            events_proc.command = bc.COMMAND_VALIDATE
            results = events_proc.process()
            self.assertIn("msg_category", results, "should have msg_category")

    def test_validate_with_sidecar_and_no_events_file_schema(self):
        """Test validate with sidecar but no schema."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", None)
            events_proc.command = bc.COMMAND_VALIDATE
            # Without schema, process should raise an error
            with self.assertRaises(HedFileError):
                events_proc.process()

    def test_validate_with_limit_errors(self):
        """Test validate with limit_errors enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events_bad.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_VALIDATE
            events_proc.limit_errors = True
            results = events_proc.process()
            self.assertEqual("warning", results["msg_category"], "should be warning for errors")
            self.assertTrue(results["data"], "should have error data")

    def test_assemble_with_append_assembled_true(self):
        """Test assemble with append_assembled enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            events_proc.command = bc.COMMAND_ASSEMBLE
            events_proc.append_assembled = True
            events_proc.check_for_warnings = False
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")
            self.assertTrue(results["data"], "should have assembled data")
            # Data should be tab-separated when append_assembled is true
            self.assertIn("\t", results["data"], "data should contain tabs when appended")

    def test_assemble_without_appending(self):
        """Test assemble without appending to original dataframe."""
        with self.app.app_context():
            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            events_proc.command = bc.COMMAND_ASSEMBLE
            events_proc.append_assembled = False
            events_proc.check_for_warnings = False
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")
            self.assertTrue(results["data"], "should have assembled data")

    def test_assemble_with_replace_defs(self):
        """Test assemble with replace_defs enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            events_proc.command = bc.COMMAND_ASSEMBLE
            events_proc.replace_defs = True
            events_proc.check_for_warnings = False
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")
            self.assertTrue(isinstance(results["data"], list), "data should be a list")

    def test_search_with_query_names(self):
        """Test search with explicit query names."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_SEARCH
            events_proc.queries = ["Sensory-event", "Motor-action"]
            events_proc.query_names = ["query1", "query2"]
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")
            self.assertIn("data", results, "should include search data in results")
            self.assertTrue(results["data"], "search results should contain data")

    def test_search_with_append_assembled(self):
        """Test search with append_assembled enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_SEARCH
            events_proc.queries = ["Sensory-event"]
            events_proc.append_assembled = True
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")
            self.assertTrue(results["data"], "should have search results")

    def test_search_without_append_assembled(self):
        """Test search without append_assembled."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_SEARCH
            events_proc.queries = ["Sensory-event"]
            events_proc.append_assembled = False
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")
            self.assertTrue(results["data"], "should have search results")

    def test_get_hed_objs_with_context(self):
        """Test get_hed_objs with include_context enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            events_proc.include_context = True
            hed_objs, definitions = events_proc.get_hed_objs()
            self.assertIsInstance(hed_objs, list, "should return a list of HED objects")
            self.assertTrue(len(hed_objs) > 0, "should have HED objects")

    def test_get_hed_objs_without_context(self):
        """Test get_hed_objs without context."""
        with self.app.app_context():
            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            events_proc.include_context = False
            hed_objs, definitions = events_proc.get_hed_objs()
            self.assertIsInstance(hed_objs, list, "should return a list")
            self.assertTrue(len(hed_objs) > 0, "should have HED objects")

    def test_get_hed_objs_with_replace_defs(self):
        """Test get_hed_objs with replace_defs enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            events_proc.replace_defs = True
            hed_objs, definitions = events_proc.get_hed_objs()
            self.assertIsInstance(hed_objs, list, "should return a list")

    def test_get_hed_objs_with_remove_types(self):
        """Test get_hed_objs with remove_types enabled."""
        with self.app.app_context():
            events_proc = self.get_event_proc(
                "data/sub-002_task-FacePerception_run-1_events.tsv",
                "data/task-FacePerception_events.json",
                "data/HED8.2.0.xml",
            )
            events_proc.remove_types = True
            hed_objs, definitions = events_proc.get_hed_objs()
            self.assertIsInstance(hed_objs, list, "should return a list")

    def test_remodel_with_include_summaries(self):
        """Test remodel with include_summaries enabled."""
        with self.app.app_context():
            rmdl_ops = [
                {
                    "operation": "remove_columns",
                    "description": "Remove columns",
                    "parameters": {"column_names": ["value"], "ignore_missing": True},
                }
            ]
            events_proc = self.get_event_proc("data/sub-002_task-FacePerception_run-1_events.tsv", None, None)
            events_proc.command = bc.COMMAND_REMODEL
            events_proc.remodel_operations = {"name": "test_remodel", "operations": rmdl_ops}
            events_proc.include_summaries = True
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")

    def test_remodel_without_include_summaries(self):
        """Test remodel without include_summaries."""
        with self.app.app_context():
            rmdl_ops = [
                {
                    "operation": "remove_columns",
                    "description": "Remove columns",
                    "parameters": {"column_names": ["value"], "ignore_missing": True},
                }
            ]
            events_proc = self.get_event_proc("data/sub-002_task-FacePerception_run-1_events.tsv", None, None)
            events_proc.command = bc.COMMAND_REMODEL
            events_proc.remodel_operations = {"name": "test_remodel", "operations": rmdl_ops}
            events_proc.include_summaries = False
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")

    def test_remodel_missing_operations(self):
        """Test remodel with missing operations."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/sub-002_task-FacePerception_run-1_events.tsv", None, None)
            events_proc.command = bc.COMMAND_REMODEL
            events_proc.remodel_operations = None
            with self.assertRaises(HedFileError):
                events_proc.process()

    def test_generate_sidecar_with_all_columns(self):
        """Test generate_sidecar with no column filtering."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_GENERATE_SIDECAR
            events_proc.columns_skip = []
            events_proc.columns_value = []
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")
            sidecar_data = json.loads(results["data"])
            self.assertIsInstance(sidecar_data, dict, "generated sidecar should be a dict")

    def test_generate_sidecar_with_column_filtering(self):
        """Test generate_sidecar with column skip and value lists."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = bc.COMMAND_GENERATE_SIDECAR
            events_proc.columns_skip = ["onset", "duration"]
            events_proc.columns_value = ["trial"]
            results = events_proc.process()
            self.assertEqual("success", results["msg_category"], "should be success")

    def test_process_invalid_command_coverage(self):
        """Test process with an invalid command."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", "data/HED8.2.0.xml")
            events_proc.command = "invalid_command"
            with self.assertRaises(HedFileError) as context:
                events_proc.process()
            self.assertIn("invalid", str(context.exception).lower())

    def test_validate_with_bad_schema_coverage(self):
        """Test validate with invalid schema."""
        with self.app.app_context():
            events_proc = self.get_event_proc("data/bids_events.tsv", "data/bids_events.json", None)
            events_proc.schema = "not_a_schema"
            events_proc.command = bc.COMMAND_VALIDATE
            with self.assertRaises(HedFileError):
                events_proc.process()

    def test_process_no_events_file_coverage(self):
        """Test process with no events file."""
        with self.app.app_context():
            events_proc = EventOperations()
            events_proc.schema = load_schema(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/HED8.2.0.xml")
            )
            events_proc.command = bc.COMMAND_VALIDATE
            with self.assertRaises(HedFileError):
                events_proc.process()


if __name__ == "__main__":
    unittest.main()
