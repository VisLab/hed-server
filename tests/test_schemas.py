import os
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request
from tests.test_web_base import TestWebBase
from hed.errors.exceptions import HedFileError
from hedweb.constants import base_constants as bc
from hedweb.process_form import ProcessForm
from hed import HedSchema, load_schema, load_schema_version
from hedweb.schema_operations import SchemaOperations


class Test(TestWebBase):

    def test_set_input_from_schemas_form_valid(self):
        from hedweb.schema_operations import SchemaOperations

        with self.app.test:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
            with open(schema_path, 'rb') as fp:
                environ = create_environ(data={bc.SCHEMA_FILE: fp,
                                               bc.SCHEMA_UPLOAD_OPTIONS: bc.SCHEMA_FILE_OPTION,
                                               bc.COMMAND_OPTION:  bc.COMMAND_CONVERT_SCHEMA})
            request = Request(environ)
            arguments = ProcessForm.get_input_from_form(request)
            schema_proc = SchemaOperations(arguments)
            schema_proc.command = bc.COMMAND_CONVERT_SCHEMA
            schema1 = schema_proc.schema
            self.assertTrue(schema1)
            self.assertIsInstance(schema1, HedSchema)
            self.assertEqual(schema_proc.command, bc.COMMAND_CONVERT_SCHEMA, "should have a command")
            self.assertFalse(schema_proc.check_for_warnings, "should have check_warnings false when not given")

    def test_schemas_process_empty(self):
        from hedweb.schema_operations import SchemaOperations
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_schemas = SchemaOperations()
                proc_schemas.process()

    def test_schemas_check(self):
    #    with (self.app.app_context()):
            # proc_schemas = SchemaOperations()
            # proc_schemas.command = bc.COMMAND_VALIDATE
            # proc_schemas.schema = load_schema_version("8.0.0")
            # results = proc_schemas.process()
            # self.assertTrue(results['data'], "HED 8.0.0 is not fully HED-3G compliant")

            # proc_schemas = SchemaOperations()
            # input_dict = {
            #     bc.COMMAND: bc.COMMAND_VALIDATE,
            #     bc.SCHEMA1: load_schema_version("8.0.0")
            # }
            # proc_schemas.set_input_from_dict(input_dict)
            # results = proc_schemas.process()
            # self.assertTrue(results['data'], "HED 8.0.0 is not fully HED-3G compliant")

        with self.app.app_context():
            proc_schemas = SchemaOperations()
            proc_schemas.command = bc.COMMAND_VALIDATE
            proc_schemas.schema = load_schema_version("8.2.0")
            results = proc_schemas.process()
            self.assertFalse(results['data'], "HED8.2.0 is HED-3G compliant")

    def test_schemas_convert_valid(self):
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.2.0.mediawiki')
        name = "HED8.2.0"
        with self.app.app_context():
            proc_schemas = SchemaOperations()
            proc_schemas.command = bc.COMMAND_CONVERT_SCHEMA
            proc_schemas.schema = load_schema(schema_path, name=name)
            results = proc_schemas.process()
            self.assertTrue(results['data'], "HED 8.2.0.mediawiki can be converted to xml")
            self.assertEqual(results['output_display_name'], "HED8.2.0.xml")

            proc_schemas = SchemaOperations()
            input_dict = {
                bc.COMMAND: bc.COMMAND_CONVERT_SCHEMA,
                bc.SCHEMA1: load_schema(schema_path, name=name)
            }
            proc_schemas.set_input_from_dict(input_dict)
            results = proc_schemas.process()
            self.assertTrue(results['data'], "HED 8.2.0.mediawiki can be converted to xml")
            self.assertEqual(results['output_display_name'], "HED8.2.0.xml")

    def test_schemas_convert_invalid(self):
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HEDbad.xml')
        display_name = 'HEDbad'
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_schemas = SchemaOperations()
                proc_schemas.command = bc.COMMAND_CONVERT_SCHEMA
                proc_schemas.schema = load_schema(schema_path, name=display_name)
                results = proc_schemas.process()
                self.assertTrue(results['data'], "Does not reach here, as it fails to load")

    def test_schemas_compare_valid(self):
        with self.app.app_context():
            proc_schemas = SchemaOperations()
            proc_schemas.command = bc.COMMAND_COMPARE_SCHEMAS
            proc_schemas.schema = load_schema_version("8.1.0")
            proc_schemas.schema2 = load_schema_version("8.2.0")
            results = proc_schemas.process()
            self.assertTrue(results['data'], "HED 8.1.0/8.2.0 can be compared")
            # Check for some differences
            self.assertTrue("Differences between 8.1.0 and 8.2.0" in results['data'])
            self.assertTrue("Ethnicity (Minor): Item Ethnicity added to Tags" in results['data'])
            self.assertTrue(
                "Dash (Patch): Suggested tag changed on Item/Object/Geometric-object/2D-shape/Dash" in results['data'])

            input_dict = {
                bc.COMMAND: bc.COMMAND_COMPARE_SCHEMAS,
                bc.SCHEMA1: load_schema_version("8.1.0"),
                bc.SCHEMA2: load_schema_version("8.2.0")
            }
            proc_schemas = SchemaOperations()
            proc_schemas.set_input_from_dict(input_dict)
            results = proc_schemas.process()
            self.assertTrue(results['data'], "HED 8.1.0/8.2.0 can be compared")

    def test_schemas_compare_identical(self):
        with self.app.app_context():
            proc_schemas = SchemaOperations()
            proc_schemas.command = bc.COMMAND_COMPARE_SCHEMAS
            proc_schemas.schema = load_schema_version("8.2.0")
            proc_schemas.schema2 = load_schema_version("8.2.0")
            results = proc_schemas.process()
            self.assertFalse(results['data'], "HED 8.2.0/8.2.0 can be compared, but are identical")

    def test_schemas_compare_invalid(self):
        with self.app.app_context():
            with self.assertRaises(HedFileError):
                proc_schemas = SchemaOperations()
                proc_schemas.command = bc.COMMAND_COMPARE_SCHEMAS
                proc_schemas.schema = load_schema_version("8.2.0")
                proc_schemas.process()

            with self.assertRaises(HedFileError):
                proc_schemas = SchemaOperations()
                proc_schemas.command = bc.COMMAND_COMPARE_SCHEMAS
                proc_schemas.schema2 = load_schema_version("8.2.0")
                proc_schemas.process()


if __name__ == '__main__':
    unittest.main()
