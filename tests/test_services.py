import os
import io
import json
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request
from tests.test_web_base import TestWebBase
from hed.schema import HedSchema, load_schema_version
from hed.models import Sidecar
from hed.errors.exceptions import HedFileError
from hedweb.constants import base_constants
from hedweb.process_services import ProcessServices


class Test(TestWebBase):
    def test_set_input_from_service_request_empty(self):
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                ProcessServices.process({})

    def test_set_input_from_service_request(self):
        with self.app.test:
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
            with open(sidecar_path, 'rb') as fp:
                sidecar_string = fp.read().decode('ascii')
            json_data = {base_constants.SIDECAR_STRING: sidecar_string, base_constants.CHECK_FOR_WARNINGS: 'on',
                         base_constants.SCHEMA_VERSION: '8.2.0', base_constants.SERVICE: 'sidecar_validate'}
            environ = create_environ(json=json_data)
            request = Request(environ)
            arguments = ProcessServices.set_input_from_request(request)
            self.assertIn(base_constants.SIDECAR, arguments, "should have a json sidecar")
            self.assertIsInstance(arguments[base_constants.SIDECAR], Sidecar, "should contain a sidecar")
            self.assertIsInstance(arguments[base_constants.SCHEMA], HedSchema, "should have a HED schema")
            self.assertEqual('sidecar_validate', arguments[base_constants.SERVICE], "should have a service request")
            self.assertTrue(arguments[base_constants.CHECK_FOR_WARNINGS], "should have check_warnings true when on")

    def test_set_column_parameters(self):
        from hedweb.process_services import ProcessServices

        arguments = {}
        params = {
            'columns_categorical': ['col1', 'col2'],
            'columns_value': ['col3', 'col4'],
            'columns_included': ['col1', 'col3', 'col5']
        }
        ProcessServices.set_column_parameters(arguments, params)

        self.assertEqual(arguments[base_constants.COLUMNS_SELECTED],
                         {'col1': True, 'col2': True, 'col3': False, 'col4': False})
        self.assertEqual(arguments[base_constants.COLUMNS_INCLUDED], ['col1', 'col3', 'col5'])
        self.assertTrue(arguments[base_constants.HAS_COLUMN_NAMES])
        self.assertFalse(arguments[base_constants.TAG_COLUMNS])

        arguments = {}
        params = {}
        ProcessServices.set_column_parameters(arguments, params)

        self.assertEqual(arguments[base_constants.COLUMNS_SELECTED], {})
        self.assertEqual(arguments[base_constants.COLUMNS_INCLUDED], [])
        self.assertTrue(arguments[base_constants.HAS_COLUMN_NAMES])
        self.assertFalse(arguments[base_constants.TAG_COLUMNS])

    def test_services_set_sidecar(self):
        path_upper = 'data/eeg_ds003654s_hed_inheritance/task-FacePerception_events.json'
        path_lower2 = 'data/eeg_ds003654s_hed_inheritance/sub-002/sub-002_task-FacePerception_events.json'
        path_lower3 = 'data/eeg_ds003654s_hed_inheritance/sub-003/sub-003_task-FacePerception_events.json'
        sidecar_path_upper = os.path.join(os.path.dirname(os.path.realpath(__file__)), path_upper)
        sidecar_path_lower2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), path_lower2)
        sidecar_path_lower3 = os.path.join(os.path.dirname(os.path.realpath(__file__)), path_lower3)

        with open(sidecar_path_upper) as f:
            data_upper = json.load(f)
        with open(sidecar_path_lower2) as f:
            data_lower2 = json.load(f)
        params2 = {base_constants.SIDECAR_STRING: [json.dumps(data_upper), json.dumps(data_lower2)]}
        arguments2 = {}
        ProcessServices.set_sidecar(arguments2, params2)
        self.assertIn(base_constants.SIDECAR, arguments2, 'should have a sidecar')
        self.assertIsInstance(arguments2[base_constants.SIDECAR], Sidecar)
        sidecar2 = arguments2[base_constants.SIDECAR]
        self.assertIn('event_type', data_upper, "should have key event_type")
        self.assertNotIn('event_type', data_lower2, "should not have event_type")
        self.assertIn('event_type', sidecar2.loaded_dict, "merged sidecar should have event_type")

        with open(sidecar_path_lower3) as f:
            data_lower3 = json.load(f)
        params3 = {base_constants.SIDECAR_STRING: [json.dumps(data_upper), json.dumps(data_lower3)]}
        arguments3 = {}
        ProcessServices.set_sidecar(arguments3, params3)
        self.assertIn(base_constants.SIDECAR, arguments3, 'should have a sidecar')
        self.assertIsInstance(arguments3[base_constants.SIDECAR], Sidecar)
        sidecar3 = arguments3[base_constants.SIDECAR]
        self.assertIn('event_type', data_upper, "should have key event_type")
        self.assertNotIn('event_type', data_lower3, "should have event_type")
        self.assertIn('event_type', sidecar3.loaded_dict, "merged sidecar should have event_type")

    def test_set_input_objects(self):
        sidecar_path = 'data/task-FacePerception_events.json'
        sidecar_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), sidecar_path)

        sidecar = Sidecar(sidecar_path)

        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'data/sub-002_task-FacePerception_run-1_events.tsv')
        with open(events_path, 'r') as fp:
            events_data = fp.read()

        from hed import TabularInput, SpreadsheetInput, HedString
        arguments = {
            base_constants.SCHEMA: load_schema_version("8.2.0"),
            base_constants.SIDECAR: sidecar,
            base_constants.TAG_COLUMNS: [4]
        }
        params = {
            base_constants.EVENTS_STRING: events_data,
            base_constants.SPREADSHEET_STRING: events_data,
            base_constants.STRING_LIST: ['Event', 'Age']
        }
        ProcessServices.set_input_objects(arguments, params)

        self.assertIsInstance(arguments[base_constants.EVENTS], TabularInput)
        self.assertIsInstance(arguments[base_constants.SPREADSHEET], SpreadsheetInput)
        self.assertEqual(len(arguments[base_constants.STRING_LIST]), 2)
        for item in arguments[base_constants.STRING_LIST]:
            self.assertIsInstance(item, HedString)

        # Raises error if tag columns not set, but it has a spreadsheet
        with self.assertRaises(KeyError):
            arguments = {}
            params = {
                base_constants.EVENTS_STRING: "",
                base_constants.SPREADSHEET_STRING: events_data,
            }
            ProcessServices.set_input_objects(arguments, params)

        arguments = {
            base_constants.SCHEMA: load_schema_version("8.2.0"),
            base_constants.SIDECAR: sidecar,
            base_constants.TAG_COLUMNS: [4]
        }
        params = {}
        ProcessServices.set_input_objects(arguments, params)

        self.assertNotIn(base_constants.EVENTS, arguments)
        self.assertNotIn(base_constants.SPREADSHEET, arguments)
        self.assertNotIn(base_constants.STRING_LIST, arguments)

    def test_set_remodel_parameters(self):
        remodel_file = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     'data/simple_reorder_rmdl.json'))
        with open(remodel_file, 'r') as fp:
            json_obj = json.load(fp)
        params = {'remodel_string': json.dumps(json_obj)}
        arguments = {}
        ProcessServices.set_remodel_parameters(arguments, params)
        self.assertTrue(arguments)
        self.assertIn('remodel_operations', arguments)
        self.assertEqual(len(arguments['remodel_operations']), 2)

        params = {}
        arguments = {}
        ProcessServices.set_remodel_parameters(arguments, params)
        self.assertFalse(arguments)
        self.assertNotIn('remodel_operations', arguments)

    def test_get_service_info(self):
        params = {
            base_constants.SERVICE: 'schema_validate',
            base_constants.EXPAND_DEFS: 'on',
            base_constants.CHECK_FOR_WARNINGS: 'off',
            base_constants.INCLUDE_DESCRIPTION_TAGS: 'on'
        }

        expected_result = {
            base_constants.SERVICE: 'schema_validate',
            base_constants.COMMAND: 'validate',
            base_constants.COMMAND_TARGET: 'schema',
            base_constants.HAS_COLUMN_NAMES: True,
            base_constants.CHECK_FOR_WARNINGS: False,
            base_constants.EXPAND_DEFS: True,
            base_constants.INCLUDE_DESCRIPTION_TAGS: True
        }

        result = ProcessServices.get_service_info(params)
        self.assertEqual(result, expected_result)

        params = {
            base_constants.SERVICE: 'get_services'
        }

        expected_result = {
            base_constants.SERVICE: 'get_services',
            base_constants.COMMAND: 'get_services',
            base_constants.COMMAND_TARGET: '',
            base_constants.HAS_COLUMN_NAMES: True,
            base_constants.CHECK_FOR_WARNINGS: False,
            base_constants.EXPAND_DEFS: False,
            base_constants.INCLUDE_DESCRIPTION_TAGS: False
        }

        result = ProcessServices.get_service_info(params)
        self.assertEqual(result, expected_result)

    def test_set_input_schema(self):
        from hed.schema import load_schema_version, HedSchema
        schema = load_schema_version("8.2.0")
        schema_as_string = schema.get_as_xml_string()

        parameters = {base_constants.SCHEMA_STRING: schema_as_string}
        result = ProcessServices.set_input_schema(parameters)
        self.assertIsInstance(result, HedSchema)

        parameters = {
            base_constants.SCHEMA_URL: 'https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml'}
        result = ProcessServices.set_input_schema(parameters)
        self.assertIsInstance(result, HedSchema)

        parameters = {base_constants.SCHEMA_VERSION: '8.2.0'}
        result = ProcessServices.set_input_schema(parameters)
        self.assertIsInstance(result, HedSchema)

        parameters = {base_constants.SCHEMA_STRING: 'invalid_schema_string'}
        with self.assertRaises(HedFileError):
            result = ProcessServices.set_input_schema(parameters)

    def test_get_services_list(self):
        with self.app.app_context():
            results = ProcessServices.get_services_list()
            self.assertIsInstance(results, dict, "services_list returns a dictionary")
            self.assertTrue(results["data"], "services_list return dictionary has a data key with non empty value")

    def test_process_services_sidecar(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/both_types_events_errors.json')
        with open(json_path) as f:
            data = json.load(f)
        json_text = json.dumps(data)
        fb = io.StringIO(json_text)
        arguments = {base_constants.SERVICE: 'sidecar_validate',
                     base_constants.SCHEMA: load_schema_version('8.2.0'),
                     base_constants.COMMAND: 'validate', base_constants.COMMAND_TARGET: 'sidecar',
                     base_constants.SIDECAR: Sidecar(files=fb, name='JSON_Sidecar')}
        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(response['error_type'],
                             'sidecar_validation services should not have a fatal error when file is invalid')
            results = response['results']
            self.assertEqual('warning', results['msg_category'],
                             "sidecar_validation services has success on bids_events.json")
            self.assertEqual(json.dumps('8.2.0'), results[base_constants.SCHEMA_VERSION], 'Version 8.2.0 was used')

    def test_process_services_sidecar_a(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        with open(json_path) as f:
            data = json.load(f)
        json_text = json.dumps(data)
        fb = io.StringIO(json_text)
        hed_schema = load_schema_version("8.2.0")
        json_sidecar = Sidecar(files=fb, name='JSON_Sidecar')
        arguments = {base_constants.SERVICE: 'sidecar_validate', base_constants.SCHEMA: hed_schema,
                     base_constants.COMMAND: 'validate', base_constants.COMMAND_TARGET: 'sidecar',
                     base_constants.SIDECAR: json_sidecar}
        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(response['error_type'],
                             'sidecar_validation services should not have a fatal error when file is invalid')
            results = response['results']
            self.assertEqual('success', results['msg_category'],
                             "sidecar_validation services has success on bids_events.json")
            self.assertEqual(json.dumps('8.2.0'), results[base_constants.SCHEMA_VERSION], 'Version 8.2.0 was used')

        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        with open(json_path) as f:
            data = json.load(f)
        json_text = json.dumps(data)
        fb = io.StringIO(json_text)
        arguments[base_constants.SIDECAR] = Sidecar(files=fb, name='JSON_Sidecar_BAD')
        with self.app.app_context():
            response = ProcessServices.process(arguments)
            self.assertFalse(response['error_type'],
                             'sidecar_validation services should not have a error when file is valid')
            results = response['results']
            self.assertTrue(results['data'], 'sidecar_validation produces errors when file not valid')
            self.assertEqual('warning', results['msg_category'], "sidecar_validation did not valid with 8.2.0")
            self.assertEqual(json.dumps('8.2.0'), results['schema_version'], 'Version 8.2.0 was used')


if __name__ == '__main__':
    unittest.main()
