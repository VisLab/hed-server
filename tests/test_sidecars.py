import os
import unittest

from hed.models import Sidecar
from hed.schema import HedSchema
from hed.schema.hed_schema_io import load_schema_version
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from hedweb.constants import base_constants
from hedweb.process_form import ProcessForm
from hedweb.sidecar_operations import SidecarOperations
from tests.test_web_base import TestWebBase


class TestSidecarOperations(TestWebBase):
    """Comprehensive test coverage for SidecarOperations class."""

    def test_one(self):
        proc = SidecarOperations()
        self.assertIsInstance(proc, SidecarOperations)

    def test_generate_input_from_sidecars_form(self):
        with self.app.app_context():
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            with open(sidecar_path, "rb") as fp:
                environ = create_environ(
                    data={
                        base_constants.SIDECAR_FILE: fp,
                        base_constants.SCHEMA_VERSION: "8.2.0",
                        base_constants.COMMAND_OPTION: base_constants.COMMAND_TO_LONG,
                    }
                )
            proc_sidecars = SidecarOperations()
            request = Request(environ)
            parameters = ProcessForm.get_input_from_form(request)
            proc_sidecars.set_input_from_dict(parameters)

            self.assertIsInstance(
                proc_sidecars.sidecar,
                Sidecar,
                "should have a JSON dictionary in sidecar list",
            )
            self.assertIsInstance(proc_sidecars.schema, HedSchema, "should have a HED schema")
            self.assertEqual(
                proc_sidecars.command,
                base_constants.COMMAND_TO_LONG,
                "should have a command",
            )
            self.assertFalse(
                proc_sidecars.check_for_warnings,
                "should have check for warnings false when not given",
            )

    def test_sidecars_process_empty_file(self):
        from hed.errors.exceptions import HedFileError

        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_sidecars = SidecarOperations()
                proc_sidecars.process()

    def test_sidecars_process_invalid(self):
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
        arguments = {
            base_constants.SCHEMA: load_schema_version("8.2.0"),
            base_constants.SIDECAR: Sidecar(files=sidecar_path, name="bids_events_bad"),
            base_constants.COMMAND: base_constants.COMMAND_TO_SHORT,
        }
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(
                isinstance(results, dict),
                "process to short should return a dictionary when errors",
            )
            self.assertEqual(
                "warning",
                results["msg_category"],
                "should give warning when JSON with errors",
            )
            self.assertTrue(results["data"], "should not convert using HED 8.2.0.xml")

    def test_sidecars_process_invalid_v2(self):
        sidecar_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/both_types_events_errors.json",
        )
        arguments = {
            base_constants.SCHEMA: load_schema_version("8.2.0"),
            base_constants.SIDECAR: Sidecar(files=sidecar_path, name="bids_events_bad"),
            base_constants.COMMAND: base_constants.COMMAND_TO_SHORT,
        }
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(
                isinstance(results, dict),
                "process to short should return a dictionary when errors",
            )
            self.assertEqual(
                "warning",
                results["msg_category"],
                "should give warning when JSON with errors",
            )
            self.assertTrue(results["data"], "should not convert using HED 8.2.0.xml")

    def test_sidecars_process_valid_to_short(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        arguments = {
            base_constants.SCHEMA: load_schema_version("8.2.0"),
            base_constants.SIDECAR: Sidecar(files=json_path, name="bids_events"),
            base_constants.EXPAND_DEFS: False,
            base_constants.COMMAND: base_constants.COMMAND_TO_SHORT,
        }

        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(
                isinstance(results, dict),
                "process to short should return a dict when no errors",
            )
            self.assertEqual(
                "success",
                results["msg_category"],
                "process to short should return success if no errors",
            )

    def test_sidecars_process_valid_to_short_defs_expanded(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        arguments = {
            base_constants.SCHEMA: load_schema_version("8.2.0"),
            base_constants.SIDECAR: Sidecar(files=json_path, name="bids_events"),
            base_constants.EXPAND_DEFS: True,
            base_constants.COMMAND: base_constants.COMMAND_TO_SHORT,
        }

        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(
                isinstance(results, dict),
                "process to short should return a dict when no errors and defs expanded",
            )
            self.assertEqual(
                "success",
                results["msg_category"],
                "process to short should return success if no errors and defs_expanded",
            )

    def test_sidecars_process_valid_to_long(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        arguments = {
            base_constants.SCHEMA: load_schema_version("8.2.0"),
            base_constants.SIDECAR: Sidecar(files=json_path, name="bids_events"),
            base_constants.EXPAND_DEFS: False,
            base_constants.COMMAND: base_constants.COMMAND_TO_LONG,
        }

        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(
                isinstance(results, dict),
                "process to long should return a dict when no errors",
            )
            self.assertEqual(
                "success",
                results["msg_category"],
                "process to long should return success when no errors",
            )

    def test_sidecars_process_valid_to_long_defs_expanded(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        arguments = {
            base_constants.SCHEMA: load_schema_version("8.2.0"),
            base_constants.SIDECAR: Sidecar(files=json_path, name="bids_events"),
            base_constants.EXPAND_DEFS: False,
            base_constants.COMMAND: base_constants.COMMAND_TO_LONG,
        }
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(
                isinstance(results, dict),
                "should return a dict when no errors and defs expanded",
            )
            self.assertEqual(
                "success",
                results["msg_category"],
                "should return success if converted when no errors and defs expanded",
            )

    def test_sidecars_convert_to_long_invalid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events_bad")
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_TO_LONG
            results = proc_sidecars.process()
            self.assertTrue(results["data"], "sidecar_convert to long results should have data key")
            self.assertEqual(
                "warning",
                results["msg_category"],
                "sidecar_convert to long msg_category should be warning for errors",
            )

    def test_sidecars_convert_to_long_valid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events")
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_TO_LONG
            results = proc_sidecars.process()
            self.assertTrue(results["data"], "sidecar_convert to long results should have data key")
            self.assertEqual(
                "success",
                results["msg_category"],
                "sidecar_convert to long msg_category should be success when no errors",
            )

    def test_sidecars_convert_to_short_invalid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events_bad")
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_TO_SHORT
            results = proc_sidecars.process()
            self.assertTrue(results["data"], "sidecar_convert results should have data key")
            self.assertEqual(
                "warning",
                results["msg_category"],
                "sidecar_convert msg_category should be warning for errors",
            )

    def test_bad_sidecar(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/both_types_events.json")
        json_sidecar = Sidecar(files=json_path, name="bids_events_bad")
        hed_schema = load_schema_version("8.2.0")
        issues = json_sidecar.validate(hed_schema)
        self.assertIsInstance(issues, list)
        self.assertEqual(len(issues), 36)

    def test_sidecars_convert_to_short_valid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events")
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_TO_SHORT
            results = proc_sidecars.process()
            self.assertTrue(results["data"], "sidecar_convert results should have data key")
            self.assertEqual(
                "success",
                results["msg_category"],
                "sidecar_convert msg_category should be success when no errors",
            )

    def test_sidecars_validate_invalid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events_bad")
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_VALIDATE
            results = proc_sidecars.process()
            self.assertTrue(
                results["data"],
                "sidecar_validate results should have a data key when validation issues",
            )
            self.assertEqual(
                "warning",
                results["msg_category"],
                "sidecar_validate msg_category should be warning when errors",
            )

    def test_sidecars_validate_invalid_multiple(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events_bad")
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_VALIDATE
            results = proc_sidecars.process()
            self.assertTrue(
                results["data"],
                "sidecar_validate results should have a data key when validation issues",
            )
            self.assertEqual(
                "warning",
                results["msg_category"],
                "sidecar_validate msg_category should be warning when errors",
            )

    def test_sidecars_validate_valid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events")
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_VALIDATE
            results = proc_sidecars.process()
            self.assertFalse(
                results["data"],
                "sidecar_validate results should not have a data key when no validation issues",
            )
            self.assertEqual(
                "success",
                results["msg_category"],
                "sidecar_validate msg_category should be success when no issues",
            )

    def test_sidecar_extract_valid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events")
            proc_sidecars.command = base_constants.COMMAND_EXTRACT_SPREADSHEET
            results = proc_sidecars.process()
            self.assertIsInstance(results, dict, "sidecar_extract should return a dict")
            self.assertEqual("success", results["msg_category"], "sidecar_extract should succeed")
            self.assertTrue(results["data"], "sidecar_extract should produce TSV data")
            self.assertIn("_extracted", results["output_display_name"], "output name should include _extracted suffix")
            self.assertTrue(results["output_display_name"].endswith(".tsv"), "output should be a .tsv file")

    def test_sidecar_extract_no_schema_required(self):
        """Extract does not require a schema."""
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events")
            proc_sidecars.command = base_constants.COMMAND_EXTRACT_SPREADSHEET
            # schema deliberately left as None
            results = proc_sidecars.process()
            self.assertEqual("success", results["msg_category"], "sidecar_extract should not need a schema")

    def test_sidecar_merge_no_spreadsheet_raises(self):
        """Merge should raise HedFileError when no spreadsheet is provided."""
        from hed.errors.exceptions import HedFileError

        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        with self.app.app_context():
            proc_sidecars = SidecarOperations()
            proc_sidecars.sidecar = Sidecar(files=json_path, name="bids_events")
            proc_sidecars.command = base_constants.COMMAND_MERGE_SPREADSHEET
            with self.assertRaises(HedFileError):
                proc_sidecars.process()

    def test_sidecar_merge_valid(self):
        """Merge a spreadsheet back into a sidecar via round-trip extract then merge."""
        import io

        from hed.models import SpreadsheetInput

        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        with self.app.app_context():
            # Step 1: extract
            sidecar = Sidecar(files=json_path, name="bids_events")
            extract_op = SidecarOperations()
            extract_op.sidecar = sidecar
            extract_op.command = base_constants.COMMAND_EXTRACT_SPREADSHEET
            extract_results = extract_op.process()
            self.assertEqual("success", extract_results["msg_category"])

            # Step 2: load the extracted TSV as a SpreadsheetInput and merge
            tsv_data = extract_results["data"]
            spreadsheet = SpreadsheetInput(
                file=io.StringIO(tsv_data),
                file_type=".tsv",
                tag_columns=[3],
                has_column_names=True,
                name="extracted.tsv",
            )
            merge_op = SidecarOperations()
            merge_op.sidecar = Sidecar(files=json_path, name="bids_events")
            merge_op.spreadsheet = spreadsheet
            merge_op.command = base_constants.COMMAND_MERGE_SPREADSHEET
            merge_results = merge_op.process()
            self.assertIsInstance(merge_results, dict, "sidecar_merge should return a dict")
            self.assertEqual("success", merge_results["msg_category"], "sidecar_merge should succeed")
            self.assertTrue(merge_results["data"], "sidecar_merge should produce JSON data")
            self.assertIn("_merged_with_spreadsheet", merge_results["output_display_name"])
            self.assertTrue(merge_results["output_display_name"].endswith(".json"))

    def test_sidecar_merge_without_sidecar(self):
        """Merge with no original sidecar creates a new one from the spreadsheet."""
        import io

        from hed.models import SpreadsheetInput

        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
        with self.app.app_context():
            # Extract first to get a valid 4-column spreadsheet
            sidecar = Sidecar(files=json_path, name="bids_events")
            extract_op = SidecarOperations()
            extract_op.sidecar = sidecar
            extract_op.command = base_constants.COMMAND_EXTRACT_SPREADSHEET
            extract_results = extract_op.process()

            tsv_data = extract_results["data"]
            spreadsheet = SpreadsheetInput(
                file=io.StringIO(tsv_data),
                file_type=".tsv",
                tag_columns=[3],
                has_column_names=True,
                name="extracted.tsv",
            )
            merge_op = SidecarOperations()
            merge_op.sidecar = None  # no original sidecar
            merge_op.spreadsheet = spreadsheet
            merge_op.command = base_constants.COMMAND_MERGE_SPREADSHEET
            merge_results = merge_op.process()
            self.assertEqual("success", merge_results["msg_category"])
            self.assertTrue(merge_results["data"])

    def test_sidecar_validate_with_external_definitions(self):
        """Test sidecar validation with external definitions."""
        from hedweb.process_service import ProcessServices
        from hedweb.sidecar_operations import SidecarOperations

        with self.app.app_context():
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/sidecar_with_defs.json")
            proc_sidecar = SidecarOperations()
            proc_sidecar.schema = load_schema_version("8.2.0")
            proc_sidecar.sidecar = Sidecar(files=sidecar_path, name="sidecar_with_defs")
            def_string = '{"definitions": "(Definition/TestDef/#, (Age/#))"}'
            proc_sidecar.definitions = ProcessServices.get_definitions(def_string, proc_sidecar.schema)
            proc_sidecar.command = base_constants.COMMAND_VALIDATE
            results = proc_sidecar.process()
            self.assertIn("msg_category", results, "should have msg_category")

    def test_sidecar_convert_with_external_definitions(self):
        """Test sidecar conversion with external definitions."""
        from hedweb.process_service import ProcessServices
        from hedweb.sidecar_operations import SidecarOperations

        with self.app.app_context():
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/sidecar_with_defs.json")
            proc_sidecar = SidecarOperations()
            proc_sidecar.schema = load_schema_version("8.2.0")
            proc_sidecar.sidecar = Sidecar(files=sidecar_path, name="sidecar_with_defs")
            def_string = '{"definitions": "(Definition/TestDef/#, (Age/#))"}'
            proc_sidecar.definitions = ProcessServices.get_definitions(def_string, proc_sidecar.schema)
            proc_sidecar.command = base_constants.COMMAND_TO_LONG
            results = proc_sidecar.process()
            self.assertIn("msg_category", results, "should have msg_category")

    # ========== COMPREHENSIVE COVERAGE TESTS ==========
    # Additional comprehensive tests for SidecarOperations from coverage file
    # Tests for sidecar_validate() method variations
    def test_validate_with_valid_sidecar_no_warnings(self):
        """Test validation of valid sidecar without checking warnings."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_VALIDATE
            sidecar_proc.check_for_warnings = False
            results = sidecar_proc.sidecar_validate()
            self.assertEqual("success", results["msg_category"], "valid sidecar should return success")

    def test_validate_with_valid_sidecar_with_warnings(self):
        """Test validation of valid sidecar while checking for warnings."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_VALIDATE
            sidecar_proc.check_for_warnings = True
            results = sidecar_proc.sidecar_validate()
            self.assertIn("msg_category", results, "should have msg_category")

    def test_validate_with_invalid_sidecar(self):
        """Test validation of invalid sidecar."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events_bad")
            sidecar_proc.command = base_constants.COMMAND_VALIDATE
            sidecar_proc.check_for_warnings = False
            results = sidecar_proc.sidecar_validate()
            self.assertEqual("warning", results["msg_category"], "invalid sidecar should return warning")

    def test_validate_result_structure(self):
        """Test that validation results have expected structure."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_VALIDATE
            results = sidecar_proc.sidecar_validate()
            self.assertIn(base_constants.COMMAND, results, "should have command key")

    def test_convert_to_short_with_valid_sidecar(self):
        """Test conversion to short form with valid sidecar."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_TO_SHORT
            results = sidecar_proc.sidecar_convert()
            self.assertEqual("success", results["msg_category"], "should succeed with valid sidecar")

    def test_convert_to_long_with_valid_sidecar(self):
        """Test conversion to long form with valid sidecar."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_TO_LONG
            results = sidecar_proc.sidecar_convert()
            self.assertEqual("success", results["msg_category"], "should succeed with valid sidecar")

    def test_convert_to_short_with_invalid_sidecar(self):
        """Test conversion to short form with invalid sidecar."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events_bad")
            sidecar_proc.command = base_constants.COMMAND_TO_SHORT
            results = sidecar_proc.sidecar_convert()
            self.assertEqual("warning", results["msg_category"], "invalid sidecar should return warning")

    def test_convert_to_long_with_invalid_sidecar(self):
        """Test conversion to long form with invalid sidecar."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events_bad.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events_bad")
            sidecar_proc.command = base_constants.COMMAND_TO_LONG
            results = sidecar_proc.sidecar_convert()
            self.assertEqual("warning", results["msg_category"], "invalid sidecar should return warning")

    def test_extract_creates_spreadsheet(self):
        """Test that extraction creates a spreadsheet."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            results = sidecar_proc.sidecar_extract()
            self.assertEqual("success", results["msg_category"], "extraction should succeed")
            self.assertTrue(results["data"], "should have extracted data")

    def test_extract_result_structure(self):
        """Test that extraction results have expected structure."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            results = sidecar_proc.sidecar_extract()
            self.assertIn(base_constants.COMMAND, results, "should have command key")

    def test_process_missing_command(self):
        """Test process raises error when command is missing."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = None
            from hed.errors import HedFileError

            with self.assertRaises(HedFileError):
                sidecar_proc.process()

    def test_process_missing_sidecar(self):
        """Test process raises error when sidecar is missing for non-merge command."""
        from hed.errors import HedFileError

        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_proc.command = base_constants.COMMAND_VALIDATE
            sidecar_proc.sidecar = None
            with self.assertRaises(HedFileError):
                sidecar_proc.process()

    def test_process_validate_command(self):
        """Test process handles validate command."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_VALIDATE
            results = sidecar_proc.process()
            self.assertIsInstance(results, dict, "should return dict")

    def test_process_to_short_command(self):
        """Test process handles to_short command."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_TO_SHORT
            results = sidecar_proc.process()
            self.assertIsInstance(results, dict, "should return dict")

    def test_process_to_long_command(self):
        """Test process handles to_long command."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_TO_LONG
            results = sidecar_proc.process()
            self.assertIsInstance(results, dict, "should return dict")

    def test_process_extract_command(self):
        """Test process handles extract command."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = base_constants.COMMAND_EXTRACT_SPREADSHEET
            results = sidecar_proc.process()
            self.assertIsInstance(results, dict, "should return dict")

    def test_process_invalid_command(self):
        """Test process raises error for invalid command."""
        from hed.errors import HedFileError

        with self.app.app_context():
            sidecar_proc = SidecarOperations()
            sidecar_proc.schema = load_schema_version("8.2.0")
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            sidecar_proc.sidecar = Sidecar(files=sidecar_path, name="bids_events")
            sidecar_proc.command = "invalid_command"
            with self.assertRaises(HedFileError):
                sidecar_proc.process()

    def test_sidecar_operations_initialization_with_none(self):
        """Test SidecarOperations can be initialized with None."""
        with self.app.app_context():
            sidecar_proc = SidecarOperations(None)
            self.assertIsNone(sidecar_proc.schema)


if __name__ == "__main__":
    unittest.main()
