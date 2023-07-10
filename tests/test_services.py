import os
import io
import json
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request
from tests.test_web_base import TestWebBase
from hed import schema as hedschema
from hed import models
from hedweb.constants import base_constants


class Test(TestWebBase):
    def test_get_input_from_service_request_empty(self):
        from hedweb.services import get_input_from_request
        self.assertRaises(TypeError, get_input_from_request, {},
                          "An exception should be raised if an empty request is passed")
        self.assertTrue(1, "Testing get_input_from_request")

    def test_get_input_from_service_request(self):
        from hed.models.sidecar import Sidecar
        from hed.schema import HedSchema
        from hedweb.services import get_input_from_request
        with self.app.test:
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
            with open(sidecar_path, 'rb') as fp:
                sidecar_string = fp.read().decode('ascii')
            json_data = {base_constants.SIDECAR_STRING: sidecar_string, base_constants.CHECK_FOR_WARNINGS: 'on',
                         base_constants.SCHEMA_VERSION: '8.0.0', base_constants.SERVICE: 'sidecar_validate'}
            environ = create_environ(json=json_data)
            request = Request(environ)
            arguments = get_input_from_request(request)
            self.assertIn(base_constants.SIDECAR, arguments, "get_input_from_request should have a json sidecar")
            self.assertIsInstance(arguments[base_constants.SIDECAR], Sidecar,
                                  "get_input_from_request should contain a sidecar")
            self.assertIsInstance(arguments[base_constants.SCHEMA], HedSchema,
                                  "get_input_from_request should have a HED schema")
            self.assertEqual('sidecar_validate', arguments[base_constants.SERVICE],
                             "get_input_from_request should have a service request")
            self.assertTrue(arguments[base_constants.CHECK_FOR_WARNINGS],
                            "get_input_from_request should have check_warnings true when on")

    def test_get_remodel_parameters(self):
        from hedweb.services import get_remodel_parameters
        remodel_file = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     'data/simple_reorder_rmdl.json'))
        with open(remodel_file, 'r') as fp:
            json_obj = json.load(fp)
        params = {'remodel_string': json.dumps(json_obj)}
        arguments = {}
        get_remodel_parameters(arguments, params)
        self.assertTrue(arguments)
        self.assertIn('remodel_operations', arguments)
        self.assertEqual(len(arguments['remodel_operations']), 2)

    def test_get_remodel_parameters_empty(self):
        from hedweb.services import get_remodel_parameters
        params = {}
        arguments = {}
        get_remodel_parameters(arguments, params)
        self.assertFalse(arguments)
        self.assertNotIn('remodel_operations', arguments)

    def test_services_process_empty(self):
        from hedweb.services import process
        with self.app.app_context():
            arguments = {'service': ''}
            response = process(arguments)
            self.assertEqual(response["error_type"], "HEDServiceMissing", "process must have a service key")

    def test_services_list(self):
        from hedweb.services import services_list
        with self.app.app_context():
            results = services_list()
            self.assertIsInstance(results, dict, "services_list returns a dictionary")
            self.assertTrue(results["data"], "services_list return dictionary has a data key with non empty value")

    def test_process_services_sidecar(self):
        from hedweb.services import process
        from hed.schema import load_schema_version
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/both_types_events_errors.json')
        with open(json_path) as f:
            data = json.load(f)
        json_text = json.dumps(data)
        fb = io.StringIO(json_text)
        hed_schema = load_schema_version('8.1.0')

        json_sidecar = models.Sidecar(files=fb, name='JSON_Sidecar')
        arguments = {base_constants.SERVICE: 'sidecar_validate', base_constants.SCHEMA: hed_schema,
                     base_constants.COMMAND: 'validate', base_constants.COMMAND_TARGET: 'sidecar',
                     base_constants.SIDECAR: json_sidecar}
        with self.app.app_context():
            response = process(arguments)
            self.assertFalse(response['error_type'],
                             'sidecar_validation services should not have a fatal error when file is invalid')
            results = response['results']
            self.assertEqual('warning', results['msg_category'],
                             "sidecar_validation services has success on bids_events.json")
            self.assertEqual(json.dumps('8.1.0'), results[base_constants.SCHEMA_VERSION], 'Version 8.1.0 was used')

    def test_process_services_sidecar_a(self):
        from hedweb.services import process
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        with open(json_path) as f:
            data = json.load(f)
        json_text = json.dumps(data)
        fb = io.StringIO(json_text)
        schema_url = 'https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/' \
                     + 'hedxml/HED8.2.0.xml'
        hed_schema = hedschema.load_schema(schema_url)
        json_sidecar = models.Sidecar(files=fb, name='JSON_Sidecar')
        arguments = {base_constants.SERVICE: 'sidecar_validate', base_constants.SCHEMA: hed_schema,
                     base_constants.COMMAND: 'validate', base_constants.COMMAND_TARGET: 'sidecar',
                     base_constants.SIDECAR: json_sidecar}
        with self.app.app_context():
            response = process(arguments)
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
        arguments[base_constants.SIDECAR] = models.Sidecar(files=fb, name='JSON_Sidecar_BAD')
        with self.app.app_context():
            response = process(arguments)
            self.assertFalse(response['error_type'],
                             'sidecar_validation services should not have a error when file is valid')
            results = response['results']
            self.assertTrue(results['data'], 'sidecar_validation produces errors when file not valid')
            self.assertEqual('warning', results['msg_category'], "sidecar_validation did not valid with 7.2.0")
            self.assertEqual(json.dumps('8.2.0'), results['schema_version'], 'Version 7.2.0 was used')

    def test_services_get_sidecar(self):
        from hedweb.services import get_sidecar
        from hed import Sidecar
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
        get_sidecar(arguments2, params2)
        self.assertIn(base_constants.SIDECAR, arguments2, 'get_sidecar arguments should have a sidecar')
        self.assertIsInstance(arguments2[base_constants.SIDECAR], Sidecar)
        sidecar2 = arguments2[base_constants.SIDECAR]
        self.assertIn('event_type', data_upper, "get_sidecar upper has key event_type")
        self.assertNotIn('event_type', data_lower2, "get_sidecar lower2 does not have event_type")
        self.assertIn('event_type', sidecar2.loaded_dict, "get_sidecar merged sidecar has event_type")

        with open(sidecar_path_lower3) as f:
            data_lower3 = json.load(f)
        params3 = {base_constants.SIDECAR_STRING: [json.dumps(data_upper), json.dumps(data_lower3)]}
        arguments3 = {}
        get_sidecar(arguments3, params3)
        self.assertIn(base_constants.SIDECAR, arguments3, 'get_sidecar arguments should have a sidecar')
        self.assertIsInstance(arguments3[base_constants.SIDECAR], Sidecar)
        sidecar3 = arguments3[base_constants.SIDECAR]
        self.assertIn('event_type', data_upper, "get_sidecar upper has key event_type")
        self.assertNotIn('event_type', data_lower3, "get_sidecar lower3 does not have event_type")
        self.assertIn('event_type', sidecar3.loaded_dict, "get_sidecar merged sidecar has event_type")


if __name__ == '__main__':
    unittest.main()
