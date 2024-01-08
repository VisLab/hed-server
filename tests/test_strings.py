import os
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from tests.test_web_base import TestWebBase
from hed.schema import HedSchema, load_schema
from hed.models import HedString
from hed.models import Sidecar
from hed.errors.exceptions import HedFileError
from hedweb.constants import base_constants


class Test(TestWebBase):
    def test_get_input_from_string_form_empty(self):
        from hedweb.process_strings import ProcessStrings
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                strings_proc = ProcessStrings()
                strings_proc.process()


    def test_get_input_from_string_form(self):
        from hedweb.process_strings import ProcessStrings
        with self.app.test:
            environ = create_environ(data={base_constants.STRING_INPUT: 'Red,Blue',
                                           base_constants.SCHEMA_VERSION: '8.0.0',
                                           base_constants.CHECK_FOR_WARNINGS: 'on',
                                           base_constants.COMMAND_OPTION: base_constants.COMMAND_VALIDATE})
            request = Request(environ)
            proc_strings = ProcessStrings()
            proc_strings.set_input_from_form(request)
            self.assertIsInstance(proc_strings.string_list, list, "should have a string list")
            self.assertIsInstance(proc_strings.schema, HedSchema, "should have a HED schema")
            self.assertEqual(proc_strings.command, base_constants.COMMAND_VALIDATE, "should have a command")
            self.assertTrue(proc_strings.check_for_warnings, "should have check_warnings true when on")

    def test_string_process(self):
        from hedweb.process_strings import ProcessStrings
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_strings = ProcessStrings()
                proc_strings.process()

    def test_string_convert_to_short_invalid(self):
        from hedweb.process_strings import ProcessStrings
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        
        with self.app.app_context():
            proc_strings = ProcessStrings()
            proc_strings.schema = load_schema(schema_path)
            proc_strings.string_list = [HedString('Red, Blech', proc_strings.schema)]
            proc_strings.command = base_constants.COMMAND_TO_SHORT
            results = proc_strings.process()
            self.assertEqual('warning', results['msg_category'], "should issue warning if unsuccessful")

    def test_string_convert_to_short_valid(self):
        from hedweb.process_strings import ProcessStrings
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        with self.app.app_context():
            proc_strings = ProcessStrings()
            proc_strings.schema = load_schema(schema_path)
            proc_strings.string_list = [HedString('Property/Informational-property/Description/Blech, Blue',
                                                  proc_strings.schema)]
            proc_strings.command = base_constants.COMMAND_TO_SHORT
            results = proc_strings.process()
            data = results['data']
            self.assertTrue(data, 'should return data')
            self.assertIsInstance(data, list, "should return a list")
            self.assertEqual("Description/Blech,Blue", data[0], "should return the correct short form.")
            self.assertEqual('success', results['msg_category'], "should return success if converted")

    def test_string_convert_to_long(self):
        from hedweb.process_strings import ProcessStrings  
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        with self.app.app_context():
            proc_strings = ProcessStrings()
            proc_strings.schema = load_schema(schema_path)
            proc_strings.string_list = [HedString('Red', proc_strings.schema), HedString('Blue', proc_strings.schema)]
            proc_strings.command = base_constants.COMMAND_TO_LONG
            results = proc_strings.process()
            self.assertEqual('success', results['msg_category'], "should return success if converted")

    def test_string_validate(self):
        from hedweb.process_strings import ProcessStrings  
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')

        with self.app.app_context():
            proc_strings = ProcessStrings()
            proc_strings.schema = load_schema(schema_path)
            proc_strings.string_list = [HedString('Red', proc_strings.schema), 
                                        HedString('Blech', proc_strings.schema)]
            proc_strings.command = base_constants.COMMAND_VALIDATE
            results = proc_strings.process()
            self.assertEqual('warning', results['msg_category'], "validate has warning if validation issues")


if __name__ == '__main__':
    unittest.main()
