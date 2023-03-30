import os
import json
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from tests.test_web_base import TestWebBase
from hed import schema as hedschema
from hed.models import Sidecar, TabularInput
from hed.errors.exceptions import HedFileError
from hedweb.constants import base_constants


class Test(TestWebBase):
    cache_schemas = True

    def test_get_input_from_events_form_empty(self):
        from hedweb.events import get_events_form_input
        self.assertRaises(TypeError, get_events_form_input, {},
                          "An exception should be raised if an empty request is passed")
        self.assertTrue(1, "Testing get_events_form_input")

    def test_get_input_from_events_form(self):
        from hed.schema import HedSchema
        from hedweb.events import get_events_form_input
        with self.app.test:
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
            events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
            with open(sidecar_path, 'rb') as fp:
                with open(events_path, 'rb') as fpe:
                    environ = create_environ(data={base_constants.SIDECAR_FILE: fp,
                                                   base_constants.SCHEMA_VERSION: '8.0.0',
                                                   base_constants.EVENTS_FILE: fpe, base_constants.EXPAND_DEFS: 'on',
                                                   base_constants.COMMAND_OPTION: base_constants.COMMAND_ASSEMBLE})
            request = Request(environ)
            arguments = get_events_form_input(request)
            self.assertIsInstance(arguments[base_constants.EVENTS], TabularInput,
                                  "get_events_form_input should have an events object")
            self.assertIsInstance(arguments[base_constants.SCHEMA], HedSchema,
                                  "get_events_form_input should have a HED schema")
            self.assertEqual(base_constants.COMMAND_ASSEMBLE, arguments[base_constants.COMMAND],
                             "get_events_form_input should have a command")
            self.assertTrue(arguments[base_constants.EXPAND_DEFS],
                            "get_events_form_input should have expand_defs true when on")

    def test_events_process_empty_file(self):
        # Test for empty events_path
        from hedweb.events import process
        arguments = {'events_path': ''}
        with self.assertRaises(HedFileError):
            process(arguments)

    def test_events_process_invalid(self):
        from hedweb.events import process
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        sidecar = Sidecar(files=sidecar_path, name='bids_events_bad')
        events = TabularInput(file=events_path, sidecar=sidecar, name='bids_events')
        arguments = {base_constants.EVENTS: events, base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                     base_constants.EXPAND_DEFS: True,
                     base_constants.CHECK_FOR_WARNINGS: True, base_constants.SCHEMA: hed_schema}
        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process validation should return a result dictionary when validation errors')
            self.assertEqual('warning', results['msg_category'],
                             'process validate should return warning when errors')

    def test_events_process_valid(self):
        from hedweb.events import process
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        sidecar = Sidecar(files=json_path, name='bids_json')
        events = TabularInput(file=events_path, sidecar=sidecar, name='bids_events')
        arguments = {base_constants.EVENTS: events, base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                     base_constants.EXPAND_DEFS: True,
                     base_constants.CHECK_FOR_WARNINGS: True, base_constants.SCHEMA: hed_schema}
        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process validation should return a dictionary when validation errors')
            self.assertEqual('success', results['msg_category'],
                             'process validate should give success when no errors')
            self.assertFalse(results["data"], 'process not return data no no errors')

    def test_events_assemble_invalid(self):
        from hedweb.events import assemble
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        sidecar = Sidecar(files=json_path, name='bids_events_bad')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        options = {'columns_included': None, 'expand_defs': True, 'check_for_warnings': False}
        events = TabularInput(file=events_path, sidecar=sidecar, name='bids_events')
        with self.app.app_context():
            results = assemble(hed_schema, events, sidecar, options)
            self.assertTrue('data' in results,
                            'assemble results should have a data key when no errors')
            self.assertEqual('warning', results["msg_category"],
                             'assemble msg_category should be warning when errors')

    def test_events_assemble_valid(self):
        from hedweb.events import assemble
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        sidecar = Sidecar(files=json_path, name='bids_json')
        events = TabularInput(file=events_path, sidecar=sidecar, name='bids_events')
        options = {'columns_included': None, 'expand_defs': True, 'check_for_warnings': False}
        with self.app.app_context():
            results = assemble(hed_schema, events, sidecar, options)
            self.assertTrue(results['data'],
                            'assemble results should have a data key when no errors')
            self.assertEqual('success', results['msg_category'],
                             'assemble msg_category should be success when no errors')

    def test_generate_sidecar_invalid(self):
        from hedweb.events import generate_sidecar
        options = {'columns_selected': {'event_type': True}}
        with self.assertRaises(AttributeError):
            with self.app.app_context():
                generate_sidecar(None, options)

    def test_generate_sidecar_valid(self):
        from hedweb.events import generate_sidecar
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        events = TabularInput(file=events_path, name='bids_events')
        options = {'columns_selected': {'event_type': True, 'bci_prediction': True, 'trial': False}}
        results = generate_sidecar(events, options)
        self.assertTrue(results['data'],
                        'generate_sidecar results should have a data key when no errors')
        self.assertEqual('success', results['msg_category'],
                         'generate_sidecar msg_category should be success when no errors')

    def test_search_invalid(self):
        from hedweb.events import search
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        sidecar = Sidecar(files=json_path, name='bids_sidecar')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        query = ""
        events = TabularInput(file=events_path, sidecar=sidecar, name='bids_events')
        with self.app.app_context():
            results = search(hed_schema, events, sidecar, query)
            self.assertTrue('data' in results, 'make_query results should have a data key when errors')
            self.assertEqual('warning', results["msg_category"],
                             'make_query msg_category should be warning when errors')

    def test_events_search_valid(self):
        from hedweb.events import search
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        sidecar = Sidecar(files=json_path, name='bids_json')
        events = TabularInput(file=events_path, sidecar=sidecar, name='bids_events')
        query = "Sensory-event"
        with self.app.app_context():
            results = search(hed_schema, events, sidecar, query)
            self.assertTrue(results['data'],
                            'make_query results should have a data key when no errors')
            self.assertEqual('success', results['msg_category'],
                             'make_query msg_category should be success when no errors')

    def test_events_validate_invalid(self):
        from hedweb.events import validate
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        sidecar = Sidecar(files=json_path, name='bids_events_bad')
        events = TabularInput(file=events_path, sidecar=sidecar, name='bids_events')
        with self.app.app_context():
            results = validate(hed_schema, events)
            self.assertTrue(results['data'],
                            'validate results should have a data key when validation errors')
            self.assertEqual('warning', results["msg_category"],
                             'validate msg_category should be warning when errors')

    def test_events_validate_valid(self):
        from hedweb.events import validate
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        sidecar = Sidecar(files=json_path, name='bids_events')
        events = TabularInput(file=events_path, sidecar=sidecar, name='bids_events')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)

        with self.app.app_context():
            results = validate(hed_schema, events)
            self.assertFalse(results['data'],
                             'validate results should not have a data key when no validation errors')
            self.assertEqual('success', results['msg_category'],
                             'validate msg_category should be success when no errors')

    def test_events_remodel_valid_no_hed(self):
        from hedweb.events import remodel
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'data/sub-002_task-FacePerception_run-1_events.tsv')
        remodel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'data/simple_reorder_rmdl.json')
        events = TabularInput(file=events_path, name='wh_events')
        df = events.dataframe
        df_rows = len(df)
        df_cols = len(df.columns)
        with open(remodel_path, 'r') as fp:
            remodel_json = json.load(fp)
        remodeler = {'name': "simple_reorder_rmdl.json", 'operations': remodel_json}
        hed_schema = None
        sidecar = None

        with self.app.app_context():
            results = remodel(hed_schema, events, sidecar, remodeler)
        self.assertTrue(results['data'], 'remodel results should have a data key when successful')
        self.assertEqual('success', results['msg_category'],'remodel msg_category should be success when no errors')
        # TODO: Test the rows and columns of result.

    def test_events_remodel_invalid_no_hed(self):
        from hedweb.events import remodel

        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'data/sub-002_task-FacePerception_run-1_events.tsv')
        remodel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'data/simple_reorder_rmdl.json')
        events = TabularInput(file=events_path, name='wh_events')
        with open(remodel_path, 'r') as fp:
            remodeler = json.load(fp)
        hed_schema = None
        sidecar = None
        operation_0 = {'badoperation': 'remove_columns', 'description': 'bad structure', 'parameters': {'ignore_missing': True}}
        operation_1 = {'operation': 'unknown_command', 'description': 'bad command', 'parameters': {'ignore_missing': True}}
        operation_2 = {'command': 'remove_columns', 'description': 'bad parameters', 'parameters': {'ignore_missing': True}}
        operation_bad = [operation_0, remodeler[0], operation_1, remodeler[1], operation_2]
        remodel_bad = {'name': 'remodel_bad.json', 'operations': operation_bad}
        with self.app.app_context():
            results = remodel(hed_schema, events, sidecar, remodel_bad)
        self.assertTrue(results['data'], 'remodel results should have a data key when unsuccessful')
        self.assertEqual('warning', results['msg_category'],'remodel msg_category should be success when no errors')


if __name__ == '__main__':
    unittest.main()
