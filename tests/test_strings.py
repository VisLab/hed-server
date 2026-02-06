import unittest

from hed.errors.exceptions import HedFileError
from hed.models import HedString
from hed.schema import HedSchema, load_schema_version
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from hedweb.constants import base_constants as bc
from hedweb.process_form import ProcessForm
from tests.test_web_base import TestWebBase


class Test(TestWebBase):
    def test_set_input_from_string_form_empty(self):
        from hedweb.string_operations import StringOperations

        with self.assertRaises(HedFileError):
            with self.app.app_context():
                strings_proc = StringOperations()
                strings_proc.process()

    def test_set_input_from_string_form(self):
        from hedweb.string_operations import StringOperations

        with self.app.test:
            environ = create_environ(
                data={
                    bc.STRING_INPUT: "Red,Blue",
                    bc.SCHEMA_VERSION: "8.2.0",
                    bc.CHECK_FOR_WARNINGS: "on",
                    bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                }
            )
            request = Request(environ)
            arguments = ProcessForm.get_input_from_form(request)
            proc_strings = StringOperations(arguments)
            self.assertIsInstance(
                proc_strings.string_list, list, "should have a string list"
            )
            self.assertIsInstance(
                proc_strings.schema, HedSchema, "should have a HED schema"
            )
            self.assertEqual(
                proc_strings.command, bc.COMMAND_VALIDATE, "should have a command"
            )
            self.assertTrue(
                proc_strings.check_for_warnings,
                "should have check_warnings true when on",
            )

    def test_set_input_with_include_prereleases_false(self):
        """Test form processing with include_prereleases=false."""
        from hedweb.string_operations import StringOperations

        with self.app.test:
            environ = create_environ(
                data={
                    bc.STRING_INPUT: "Red,Blue",
                    bc.SCHEMA_VERSION: "8.2.0",
                    "include_prereleases": "false",
                    bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                }
            )
            request = Request(environ)
            arguments = ProcessForm.get_input_from_form(request)
            proc_strings = StringOperations(arguments)
            self.assertIsInstance(
                proc_strings.schema, HedSchema, "should have a HED schema"
            )
            # Schema should be loaded successfully
            self.assertIsNotNone(proc_strings.schema)

    def test_set_input_with_include_prereleases_true(self):
        """Test form processing with include_prereleases=true."""
        from hedweb.string_operations import StringOperations

        with self.app.test:
            environ = create_environ(
                data={
                    bc.STRING_INPUT: "Red,Blue",
                    bc.SCHEMA_VERSION: "8.2.0",
                    "include_prereleases": "true",
                    bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                }
            )
            request = Request(environ)
            arguments = ProcessForm.get_input_from_form(request)
            proc_strings = StringOperations(arguments)
            self.assertIsInstance(
                proc_strings.schema, HedSchema, "should have a HED schema"
            )
            # Schema should be loaded successfully
            self.assertIsNotNone(proc_strings.schema)

    def test_string_process(self):
        from hedweb.string_operations import StringOperations

        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_strings = StringOperations()
                proc_strings.process()

    def test_string_convert_to_short_invalid(self):
        from hedweb.string_operations import StringOperations

        with self.app.app_context():
            proc_strings = StringOperations()
            proc_strings.schema = load_schema_version("8.2.0")
            proc_strings.string_list = [HedString("Red, Blech", proc_strings.schema)]
            proc_strings.command = bc.COMMAND_TO_SHORT
            results = proc_strings.process()
            self.assertEqual(
                "warning",
                results["msg_category"],
                "should issue warning if unsuccessful",
            )

    def test_string_convert_to_short_valid(self):
        from hedweb.string_operations import StringOperations

        with self.app.app_context():
            proc_strings = StringOperations()
            proc_strings.schema = load_schema_version("8.2.0")
            proc_strings.string_list = [
                HedString(
                    "Property/Informational-property/Description/Blech, Blue",
                    proc_strings.schema,
                )
            ]
            proc_strings.command = bc.COMMAND_TO_SHORT
            results = proc_strings.process()
            data = results["data"]
            self.assertTrue(data, "should return data")
            self.assertIsInstance(data, list, "should return a list")
            self.assertEqual(
                "Description/Blech,Blue",
                data[0],
                "should return the correct short form.",
            )
            self.assertEqual(
                "success", results["msg_category"], "should return success if converted"
            )

    def test_string_convert_to_long(self):
        from hedweb.string_operations import StringOperations

        with self.app.app_context():
            proc_strings = StringOperations()
            proc_strings.schema = load_schema_version("8.2.0")
            proc_strings.string_list = [
                HedString("Red", proc_strings.schema),
                HedString("Blue", proc_strings.schema),
            ]
            proc_strings.command = bc.COMMAND_TO_LONG
            results = proc_strings.process()
            self.assertEqual(
                "success", results["msg_category"], "should return success if converted"
            )

    def test_string_search(self):
        from hedweb.string_operations import StringOperations

        with self.app.app_context():
            proc_strings = StringOperations()
            proc_strings.schema = load_schema_version("8.2.0")
            proc_strings.string_list = [
                HedString("Red", proc_strings.schema),
                HedString("Blue", proc_strings.schema),
            ]
            proc_strings.command = bc.COMMAND_SEARCH
            proc_strings.query_names = None
            proc_strings.request_from = "from_service"
            proc_strings.queries = "Red"
            results = proc_strings.process()
            self.assertEqual(
                "success", results["msg_category"], "should return success if converted"
            )

    def test_string_validate(self):
        from hedweb.string_operations import StringOperations

        with self.app.app_context():
            proc_strings = StringOperations()
            proc_strings.schema = load_schema_version("8.2.0")
            proc_strings.string_list = [
                HedString("Red", proc_strings.schema),
                HedString("Blech", proc_strings.schema),
            ]
            proc_strings.command = bc.COMMAND_VALIDATE
            results = proc_strings.process()
            self.assertEqual(
                "warning",
                results["msg_category"],
                "validate has warning if validation issues",
            )


if __name__ == "__main__":
    unittest.main()
