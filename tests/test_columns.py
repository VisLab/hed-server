import unittest
from tests.test_web_base import TestWebBase
import io
import os
from hedweb.constants import base_constants as bc
import openpyxl
from pandas import DataFrame
from werkzeug.datastructures import FileStorage
from werkzeug.wrappers import Request
from werkzeug.test import create_environ


class Test(TestWebBase):

    def test_create_column_selections(self):
        from hedweb.columns import create_column_selections
        form_dict = {'column_1_use': 'on', 'column_1_name': 'event_type', 'column_1_category': 'on',
                     'column_2_name': 'event_num',
                     'column_3_use': 'on', 'column_3_name': 'event_test',
                     'column_4_use': 'on', 'column_4_category': 'on',
                     'column_5_use': 'on', 'column_5_name': 'event_type_blech', 'column_5_category': 'on'}
        column_selections = create_column_selections(form_dict)
        self.assertTrue(column_selections['event_type'], 'event_type should be a category column')
        self.assertNotIn('event_num', column_selections, 'event_num not used so should not be in column_selections')
        self.assertFalse(column_selections['event_test'], 'event_test is not a category column')
        self.assertTrue(column_selections['event_type_blech'], 'event_type_blech should be a category column')
        self.assertEqual(len(column_selections.keys()), 3, 'column must have both a _use and a _name')

    def test_create_columns_info(self):
        from hedweb.columns import _create_columns_info
        csv_content = "A\tB\n1\t4\n2\t5\n3\t6"
        columns_file = io.StringIO(csv_content)
        columns_file.filename = 'test.tsv'

        result = _create_columns_info(columns_file, has_column_names=True)
        self.assertEqual(result[bc.COLUMNS_FILE], 'test.tsv')
        self.assertListEqual(result[bc.COLUMN_LIST], ['A', 'B'])

        excel_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        with open(excel_file_path, 'rb') as file:
            columns_file = file
            columns_file.filename = os.path.basename(excel_file_path)

            result = _create_columns_info(columns_file, has_column_names=True)
            self.assertEqual(result[bc.COLUMNS_FILE], 'ExcelMultipleSheets.xlsx')
            self.assertListEqual(result[bc.COLUMN_LIST],
                                 ['Event code', 'Short label', 'Long name', 'Description in text', 'HED tags'])
            self.assertEqual(result[bc.WORKSHEET_SELECTED], "LKT 8HED3")

        with open(excel_file_path, 'rb') as file:
            columns_file = file
            columns_file.filename = os.path.basename(excel_file_path)

            result = _create_columns_info(columns_file, has_column_names=True, sheet_name="DAS Events")
            self.assertEqual(result[bc.COLUMNS_FILE], 'ExcelMultipleSheets.xlsx')
            self.assertListEqual(result[bc.COLUMN_LIST],
                                 ['Event code', 'Short label', 'Description in text', 'Event category', 'HED tags'])
            self.assertEqual(result[bc.WORKSHEET_SELECTED], "DAS Events")

    def test_dataframe_from_worksheet_with_column_names(self):
        from hedweb.columns import dataframe_from_worksheet
        excel_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        workbook = openpyxl.load_workbook(excel_file_path)
        worksheet = workbook.active

        result = dataframe_from_worksheet(worksheet, has_column_names=True)
        self.assertIsInstance(result, DataFrame)
        self.assertTrue('Event code' in result.columns)  # Replace with actual column header

        # Test no column names
        result = dataframe_from_worksheet(worksheet, has_column_names=False)

        self.assertIsInstance(result, DataFrame)
        self.assertTrue(isinstance(result.columns[0], int))  # Default integer column names

    def test_get_columns_request_excel(self):
        from hedweb.columns import get_columns_request
        excel_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        with open(excel_file_path, 'rb') as file:
            valid_excel_file = FileStorage(stream=file, filename='valid_excel.xlsx')
            input_dict = {
                bc.COLUMNS_FILE: valid_excel_file,
                bc.WORKSHEET_SELECTED: "DAS Events"
            }
            environ = create_environ(data=input_dict)
            request = Request(environ)
            result = get_columns_request(request)
            self.assertIn(bc.COLUMNS_FILE, result)
            self.assertIn(bc.COLUMN_LIST, result)
            self.assertEqual(result[bc.COLUMNS_FILE], 'valid_excel.xlsx')

    def test_get_column_names(self):
        from hedweb.columns import get_column_numbers
        form_dict = {
            'column_1_check': 'on',
            'column_2_check': 'off',
            'column_3_check': 'on',
            'another_field': 'value'
        }
        result = get_column_numbers(form_dict)
        self.assertEqual(result, [1, 3])
        form_dict = {
            'column_1_check': 'off',
            'column_2_check': 'off',
            'another_field': 'value'
        }
        result = get_column_numbers(form_dict)
        self.assertEqual(result, [])

        with self.assertRaises(ValueError):
            form_dict = {
                'column_bad_check': 'on',
                'column_2_check': 'on',
                'another_field': 'value'
            }
            result = get_column_numbers(form_dict)


if __name__ == '__main__':
    unittest.main()
