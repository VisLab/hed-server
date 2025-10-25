import os
import unittest

from hed import Sidecar, load_schema_version
from hed.errors.exceptions import HedFileError
from hed.models import SpreadsheetInput
from hed.schema import HedSchema
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from hedweb.constants import base_constants as bc
from hedweb.process_form import ProcessForm
from hedweb.spreadsheet_operations import SpreadsheetOperations
from tests.test_web_base import TestWebBase


class Test(TestWebBase):

    @staticmethod
    def get_spread_proc(spread_file, schema_version="8.2.0", worksheet=None, tag_columns=None):
        spread_proc = SpreadsheetOperations()
        spread_proc.worksheet = worksheet
        spread_proc.tag_columns = tag_columns
        spread_proc.has_column_names = True
        if spread_file:
            spread_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), spread_file)
            spread_proc.spreadsheet = SpreadsheetInput(spread_path, worksheet_name=worksheet,
                                                       tag_columns=tag_columns, has_column_names=True,
                                                       column_prefix_dictionary=None, name=spread_file)
        if schema_version:
            spread_proc.schema = load_schema_version(schema_version)
        return spread_proc

    def test_spreadsheets_empty_file(self):
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                spread_proc = self.get_spread_proc(None, None)
                spread_proc.process()

    def test_set_input_from_spreadsheets_form(self):
        with self.app.test:
            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelOneSheet.xlsx')
            with open(spreadsheet_path, 'rb') as fp:
                environ = create_environ(data={bc.SPREADSHEET_FILE: fp,
                                               bc.SCHEMA_VERSION: '8.2.0',
                                               'column_4_use': 'on',
                                               'column_4_name': 'HED tags',
                                               bc.WORKSHEET_NAME: 'LKT 8HED3',
                                               bc.HAS_COLUMN_NAMES: 'on',
                                               bc.COMMAND_OPTION: bc.COMMAND_VALIDATE})

            request = Request(environ)
            parameters = ProcessForm.get_input_from_form(request)
            spread_proc = SpreadsheetOperations(arguments=parameters)
            self.assertIsInstance(spread_proc.spreadsheet, SpreadsheetInput, "should have an spreadsheet object")
            self.assertIsInstance(spread_proc.schema, HedSchema, "should have a HED schema")
            self.assertEqual(spread_proc.command, bc.COMMAND_VALIDATE, "should have a command")
            self.assertEqual(spread_proc.worksheet, 'LKT 8HED3', "should have a sheet_name name")
            self.assertTrue(spread_proc.has_column_names, "should have column names")

    def test_set_input_from_spreadsheets_form_other(self):
        with self.app.test:
            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelOneSheet.xlsx')
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.2.0.xml')
            with open(spreadsheet_path, 'rb') as fp:
                with open(schema_path, 'rb') as sp:
                    environ = create_environ(data={bc.SPREADSHEET_FILE: fp,
                                                   bc.SCHEMA_VERSION: bc.OTHER_VERSION_OPTION,
                                                   bc.SCHEMA_PATH: sp,
                                                   'column_4_use': 'on',
                                                   'column_4_name': 'HED tags',
                                                   bc.WORKSHEET_NAME: 'LKT 8HED3',
                                                   bc.HAS_COLUMN_NAMES: 'on',
                                                   bc.COMMAND_OPTION: bc.COMMAND_VALIDATE})

            request = Request(environ)
            parameters = ProcessForm.get_input_from_form(request)
            spread_proc = SpreadsheetOperations(arguments=parameters)
            self.assertIsInstance(spread_proc.spreadsheet, SpreadsheetInput, "should have an spreadsheet object")
            self.assertIsInstance(spread_proc.schema, HedSchema, "should have a HED schema")
            self.assertEqual(spread_proc.command, bc.COMMAND_VALIDATE, "should have a command")
            self.assertEqual(spread_proc.worksheet, 'LKT 8HED3', "should have a sheet_name name")
            self.assertTrue(spread_proc.has_column_names, "should have column names")

    def test_spreadsheets_process_validate_invalid(self):
        with self.app.app_context():
            spread_proc = self.get_spread_proc('data/ExcelMultipleSheets.xlsx',
                                               worksheet='LKT Events', tag_columns=[4])
            spread_proc.command = bc.COMMAND_VALIDATE
            results = spread_proc.process()
            self.assertTrue(isinstance(results, dict),
                            'process validate should return a dictionary when errors')
            self.assertEqual('warning', results['msg_category'], 'should give warning when spreadsheet has errors')
            self.assertTrue(results['data'], 'should return validation issues using HED 8.2.0')

    def test_spreadsheets_validate_valid(self):
        with self.app.app_context():
            spread_proc = self.get_spread_proc('data/ExcelMultipleSheets.xlsx',
                                               worksheet='LKT 8HED3A', tag_columns=[4])
            spread_proc.command = bc.COMMAND_VALIDATE
            spread_proc.check_for_warnings = True
            results = spread_proc.process()
            self.assertTrue(isinstance(results, dict), "should return a dict when no errors")
            self.assertEqual('success', results['msg_category'], "should return success if validated")

    def test_spreadsheets_convert_to_long_excel(self):
        with self.app.app_context():
            spread_proc = self.get_spread_proc('data/ExcelMultipleSheets.xlsx',
                                               worksheet='LKT 8HED3A', tag_columns=[4])
            spread_proc.command = bc.COMMAND_TO_LONG
            spread_proc.check_for_warnings = True
            tags1 = spread_proc.spreadsheet.dataframe.iloc[0, 4]
            results = spread_proc.process()
            tags2 = results['spreadsheet'].dataframe.iloc[0, 4]
            self.assertGreater(len(tags2), len(tags1))
            self.assertFalse(results['data'], 'should not have a data key')
            self.assertEqual('success', results["msg_category"], 'should be success when no errors')

    def test_spreadsheets_convert_to_long_no_prefixes(self):
        with self.app.app_context():
            spread_proc = self.get_spread_proc('data/ExcelMultipleSheets.xlsx',
                                               worksheet='LKT 8HED3A', tag_columns=[4])
            spread_proc.command = bc.COMMAND_TO_LONG
            spread_proc.check_for_warnings = False
            tags1 = spread_proc.spreadsheet.dataframe.iloc[0, 4]
            results = spread_proc.process()
            self.assertTrue(isinstance(results, dict), 'should return a dict when no errors')
            self.assertEqual('success', results['msg_category'],
                             'process should return success if validated')
            tags2 = results['spreadsheet'].dataframe.iloc[0, 4]
            self.assertGreater(len(tags2), len(tags1))

    def test_spreadsheets_validate_valid_excel(self):
        with self.app.app_context():
            spread_proc = self.get_spread_proc('data/ExcelMultipleSheets.xlsx',
                                               worksheet='LKT 8HED3A', tag_columns=[4])
            spread_proc.command = bc.COMMAND_VALIDATE
            spread_proc.check_for_warnings = False
            results = spread_proc.process()

            self.assertFalse(results['data'], 'should not have a data key when no validation issues')
            self.assertEqual('success', results["msg_category"], 'should be success when no errors')

    def test_spreadsheets_validate_valid_excel1(self):
        with self.app.app_context():
            spread_proc = self.get_spread_proc('data/ExcelMultipleSheets.xlsx',
                                               worksheet='LKT 8HED3A', tag_columns=[4])
            spread_proc.command = bc.COMMAND_VALIDATE
            spread_proc.check_for_warnings = False
            results = spread_proc.process()
            self.assertFalse(results['data'], 'should have empty data when no errors')
            self.assertEqual('success', results['msg_category'], 'should be success when no errors')

    def test_spreadsheets_validate_invalid_excel(self):
        with self.app.app_context():
            spread_proc = self.get_spread_proc('data/ExcelMultipleSheets.xlsx',
                                               worksheet='LKT Events', tag_columns=[4])
            spread_proc.command = bc.COMMAND_VALIDATE
            spread_proc.check_for_warnings = False
            results = spread_proc.process()
            self.assertTrue(results['data'], 'should have data when errors')
            self.assertEqual('warning', results['msg_category'], 'should be warning when errors')

    def test_spreadsheet_validate_definitions(self):
        spread_proc = self.get_spread_proc('data/spreadsheet_with_defs.tsv', tag_columns=[2])
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/def_test.json")
        spread_proc.definitions = Sidecar(sidecar_path).extract_definitions(spread_proc.schema)
        spread_proc.command = bc.COMMAND_VALIDATE
        results = spread_proc.process()
        self.assertFalse(results['data'], 'should have empty data when no errors')
        self.assertEqual('success', results['msg_category'], 'should be success when no errors')

    def test_spreadsheet_validate_definitions_missing(self):
        spread_proc = self.get_spread_proc('data/spreadsheet_with_defs.tsv', tag_columns=[2])
        spread_proc.command = bc.COMMAND_VALIDATE
        results = spread_proc.process()
        self.assertTrue(results['data'], 'should have data when errors')
        self.assertEqual('warning', results['msg_category'], 'should be warning when errors')


if __name__ == '__main__':
    unittest.main()
