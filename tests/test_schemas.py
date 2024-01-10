import os
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request
from tests.test_web_base import TestWebBase
from hed.errors.exceptions import HedFileError
from hedweb.constants import base_constants
from hed import HedSchema, load_schema

class Test(TestWebBase):


    def test_set_input_from_schemas_form_valid(self):
        from hedweb.process_schemas import ProcessSchemas

        with self.app.test:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
            with open(schema_path, 'rb') as fp:
                environ = create_environ(data={base_constants.SCHEMA_FILE: fp,
                                               base_constants.SCHEMA_UPLOAD_OPTIONS: base_constants.SCHEMA_FILE_OPTION,
                                               base_constants.COMMAND_OPTION:  base_constants.COMMAND_CONVERT_SCHEMA})
            request = Request(environ)
            schema_proc = ProcessSchemas()
            schema_proc.set_input_from_form(request)
            # ----temporary
            schema_proc.command = base_constants.COMMAND_CONVERT_SCHEMA
            schema1_dict = schema_proc.schema
            self.assertTrue(schema1_dict)
            self.assertFalse(schema1_dict["issues"])
            self.assertIsInstance(schema1_dict["schema"], HedSchema)

            self.assertEqual(schema_proc.command, base_constants.COMMAND_CONVERT_SCHEMA, "should have a command")
            self.assertFalse(schema_proc.check_for_warnings, "should have check_warnings false when not given")

    def test_schemas_process_empty(self):
        from hedweb.process_schemas import ProcessSchemas  
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_schemas = ProcessSchemas()
                proc_schemas.process()

    def test_schemas_check(self):
        from hedweb.process_schemas import ProcessSchemas
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        with self.app.app_context():
            proc_schemas = ProcessSchemas()
            proc_schemas.command = base_constants.COMMAND_VALIDATE
            proc_schemas.schema = {"schema": load_schema(schema_path), "name": 'HED8.0.0', 
                                   "type": '.xml', "issues": {}}
            results = proc_schemas.process()
            self.assertTrue(results['data'], "HED 8.0.0 is not fully HED-3G compliant")

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.2.0.xml')
        with self.app.app_context():
            proc_schemas = ProcessSchemas()
            proc_schemas.command = base_constants.COMMAND_VALIDATE
            proc_schemas.schema = {"schema": load_schema(schema_path), "name": 'HED8.2.0',
                                   "type": '.xml', "issues": {}}
            results = proc_schemas.process()
            self.assertFalse(results['data'], "HED8.0.0 is HED-3G compliant")

    def test_schemas_convert_valid(self):
        from hedweb.process_schemas import ProcessSchemas
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.2.0.mediawiki')
        with self.app.app_context():
            proc_schemas = ProcessSchemas()
            proc_schemas.command = base_constants.COMMAND_CONVERT_SCHEMA
            proc_schemas.schema = {"schema": load_schema(schema_path), "name": 'HED8.2.0',
                                   "type": '.mediawiki', "issues": {}}
            results = proc_schemas.process()
            self.assertTrue(results['data'], "HED 8.0.0.mediawiki can be converted to xml")

    def test_schemas_convert_invalid(self):
        pass
        # from hedweb.process_schemas import ProcessSchemas
        # schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HEDbad.xml')
        # display_name = 'HEDbad'
        # with self.assertRaises(HedFileError):
        #     with self.app.app_context():
        #         hed_schema = load_schema(schema_path)
        #         schema_convert(hed_schema, display_name, '.xml')


if __name__ == '__main__':
    unittest.main()
