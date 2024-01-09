import os
import json
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from tests.test_web_base import TestWebBase
from hed.schema import HedSchema, load_schema
from hed.models import Sidecar, TabularInput
from hed.errors.exceptions import HedFileError
from hedweb.constants import base_constants


class Test(TestWebBase):
    cache_schemas = True
    
    def get_event_proc(self, events_file, sidecar_file, schema_path):
        from hedweb.process_events import ProcessEvents
        events_proc = ProcessEvents()
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), events_file)
        events_proc.schema = load_schema(schema_path)
        if sidecar_file:
            events_proc.sidecar = Sidecar(files=os.path.join(os.path.dirname(os.path.abspath(__file__)), sidecar_file))
        if events_path:
            events_proc.events = TabularInput(file=os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                                events_file), sidecar=events_proc.sidecar)
        events_proc.expand_defs = True
        events_proc.columns_included = None
        events_proc.check_for_warnings = True
        return events_proc

    def test_get_input_from_events_form_empty(self):
        from hedweb.process_events import ProcessEvents
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_events = ProcessEvents()
                proc_events.process()

    def test_get_input_from_events_form(self):
        from hedweb.process_events import ProcessEvents
        from hed.schema import HedSchema
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        with self.app.app_context():

            with open(sidecar_path, 'rb') as fp:
                with open(events_path, 'rb') as fpe:
                    environ = create_environ(data={base_constants.SIDECAR_FILE: fp,
                                                   base_constants.SCHEMA_VERSION: '8.0.0',
                                                   base_constants.EVENTS_FILE: fpe, base_constants.EXPAND_DEFS: 'on',
                                                   base_constants.COMMAND_OPTION: base_constants.COMMAND_ASSEMBLE})
            request = Request(environ)
            event_proc = ProcessEvents()
            event_proc.set_input_from_form(request)
            self.assertIsInstance(event_proc.events, TabularInput,"should have an events object")
            self.assertIsInstance(event_proc.schema, HedSchema,"should have a HED schema")
            self.assertEqual(event_proc.command, base_constants.COMMAND_ASSEMBLE,"should have correct command")
            self.assertTrue(event_proc.expand_defs, "should have expand_defs true when on")

    def test_events_process_empty_file(self):
        from hedweb.process_events import ProcessEvents
        with self.assertRaises(HedFileError):
            proc_events = ProcessEvents()
            proc_events.process()

    def test_events_process_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events_bad.json', 'data/HED8.0.0.xml')
            events_proc.command = base_constants.COMMAND_VALIDATE
            results = events_proc.process()
            self.assertTrue(isinstance(results, dict),
                            'process validation should return a result dictionary when validation errors')
            self.assertEqual('warning', results['msg_category'],
                             'process validate should return warning when errors')

    def test_events_process_valid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.0.0.xml')
            events_proc.command = base_constants.COMMAND_VALIDATE
            results = events_proc.process()
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertEqual('success', results['msg_category'], "should give success when no errors")
            self.assertFalse(results["data"], 'process not return data no no errors')

    def test_events_assemble_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events_bad.json', 'data/HED8.0.0.xml')
            events_proc.check_for_warnings = False
            events_proc.command = base_constants.COMMAND_ASSEMBLE
            results = events_proc.process()
            self.assertTrue('data' in results,'should have a data key when no errors')
            self.assertEqual('warning', results["msg_category"], 'should be warning when errors')

    def test_events_assemble_valid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.0.0.xml')
            events_proc.check_for_warnings = False
            events_proc.command = base_constants.COMMAND_ASSEMBLE
            results = events_proc.process()
            self.assertTrue(results['data'], "should have a data key when no errors")
            self.assertEqual('success', results['msg_category'], "should be success when no errors")

    def test_generate_sidecar_invalid(self):
        from hedweb.process_events import ProcessEvents
        options = {'columns_selected': {'event_type': True}}
        with self.assertRaises(AttributeError):
            with self.app.app_context():
                events_proc = self.get_event_proc('data/bids_events.tsv', '', 'data/HED8.0.0.xml')
                events_proc.command = base_constants.COMMAND_GENERATE_SIDECAR
                results = events_proc.process()

    def test_generate_sidecar_valid(self):
        from hedweb.process_events import ProcessEvents
        events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.0.0.xml')
        events_proc.columns_selected = {'event_type': True, 'bci_prediction': True, 'trial': False}
        events_proc.command = base_constants.COMMAND_GENERATE_SIDECAR
        events_proc.expand_defs = True
        events_proc.columns_included = None
        events_proc.check_for_warnings = False
        results = events_proc.process()
        self.assertTrue(results['data'],
                        'generate_sidecar results should have a data key when no errors')
        self.assertEqual('success', results['msg_category'],
                         'generate_sidecar msg_category should be success when no errors')

    def test_search_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.0.0.xml')
            events_proc.query = ""
            events_proc.command = base_constants.COMMAND_SEARCH
            results = events_proc.process()
            self.assertTrue('data' in results, 'make_query results should have a data key when errors')
            self.assertEqual('warning', results["msg_category"],
                             'make_query msg_category should be warning when errors')

    def test_events_search_valid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.0.0.xml')
            events_proc.command = base_constants.COMMAND_SEARCH
            events_proc.query = "Sensory-event"
            results = events_proc.process()
            self.assertTrue(results['data'], 'should have a data key when no errors')
            self.assertEqual('success', results['msg_category'], 'should be success when no errors')

    def test_events_validate_invalid(self):
        from hedweb.process_events import ProcessEvents
        events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events_bad.json', 'data/HED8.0.0.xml')
        events_proc.command = base_constants.COMMAND_VALIDATE
        with self.app.app_context():
            results = events_proc.process()
            self.assertTrue(results['data'], 'should have a data key when validation errors')
            self.assertEqual('warning', results["msg_category"],'should be warning when errors')

    def test_events_validate_valid(self):
        from hedweb.process_events import ProcessEvents
        events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.0.0.xml')
        events_proc.command = base_constants.COMMAND_VALIDATE
        with self.app.app_context():
            results = events_proc.process()
            self.assertFalse(results['data'], 'should not have a data key when no validation errors')
            self.assertEqual('success', results['msg_category'], 'should be success when no errors')

    # def test_events_remodel_valid_no_hed(self):
    #     events_proc = self.get_event_proc('data/sub-002_task-FacePerception_run-1_events.tsv', None, None)
    #     events_proc.command = base_constants.COMMAND_REMODEL
    #     
    #     remodel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    #                                 'data/simple_reorder_rmdl.json')
    #     df = events_proc.events.dataframe
    #     df_rows = len(df)
    #     df_cols = len(df.columns)
    #     with open(remodel_path, 'r') as fp:
    #         remodel_json = json.load(fp)
    #     remodeler = {'name': "simple_reorder_rmdl.json", 'operations': remodel_json}
    #     hed_schema = None
    #     sidecar = None
    # 
    #     with self.app.app_context():
    #         results = remodel(hed_schema, events, sidecar, remodeler)
    #     self.assertTrue(results['data'], 'remodel results should have a data key when successful')
    #     self.assertEqual('success', results['msg_category'], 'remodel msg_category should be success when no errors')
    #     # TODO: Test the rows and columns of result.

    # def test_events_remodel_invalid_no_hed(self):
    #     from hedweb.process_events import ProcessEvents
    #     events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    #                                'data/sub-002_task-FacePerception_run-1_events.tsv')
    #     remodel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    #                                 'data/simple_reorder_rmdl.json')
    #     events = TabularInput(file=events_path, name='wh_events')
    #     with open(remodel_path, 'r') as fp:
    #         remodeler = json.load(fp)
    #     hed_schema = None
    #     sidecar = None
    #     operation_0 = {'badoperation': 'remove_columns', 'description': 'bad structure',
    #                    'parameters': {'ignore_missing': True}}
    #     operation_1 = {'operation': 'unknown_command', 'description': 'bad command',
    #                    'parameters': {'ignore_missing': True}}
    #     operation_2 = {'command': 'remove_columns', 'description': 'bad parameters',
    #                    'parameters': {'ignore_missing': True}}
    #     operation_bad = [operation_0, remodeler[0], operation_1, remodeler[1], operation_2]
    #     remodel_bad = {'name': 'remodel_bad.json', 'operations': operation_bad}
    #     with self.app.app_context():
    #         results = remodel(hed_schema, events, sidecar, remodel_bad)
    #     self.assertTrue(results['data'], 'remodel results should have a data key when unsuccessful')
    #     self.assertEqual('warning', results['msg_category'], 'remodel msg_category should be success when no errors')


if __name__ == '__main__':
    unittest.main()
