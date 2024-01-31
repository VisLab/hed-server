import os
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request
from tests.test_web_base import TestWebBase
from hed.models import Sidecar
from hed.schema import HedSchema
from hed.schema.hed_schema_io import load_schema, load_schema_version
from hedweb.constants import base_constants
from hedweb.process_sidecars import ProcessSidecars


class Test(TestWebBase):

    def test_one(self):
        proc = ProcessSidecars()
        self.assertIsInstance(proc, ProcessSidecars)

    def test_generate_input_from_sidecars_form(self):
        with self.app.app_context():
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
            with open(sidecar_path, 'rb') as fp:
                environ = create_environ(data={base_constants.SIDECAR_FILE: fp, base_constants.SCHEMA_VERSION: '8.2.0',
                                               base_constants.COMMAND_OPTION: base_constants.COMMAND_TO_LONG})
            proc_sidecars = ProcessSidecars()
            request = Request(environ)
            proc_sidecars.set_input_from_form(request)

            self.assertIsInstance(proc_sidecars.sidecar, Sidecar, "should have a JSON dictionary in sidecar list")
            self.assertIsInstance(proc_sidecars.schema, HedSchema, "should have a HED schema")
            self.assertEqual(proc_sidecars.command, base_constants.COMMAND_TO_LONG, "should have a command")
            self.assertFalse(proc_sidecars.check_for_warnings, "should have check for warnings false when not given")

    def test_sidecars_process_empty_file(self):
        from hed.errors.exceptions import HedFileError
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_sidecars = ProcessSidecars()
                proc_sidecars.process()

    def test_sidecars_process_invalid(self):
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        arguments = {base_constants.SCHEMA: load_schema_version("8.2.0"),
                     base_constants.SIDECAR: Sidecar(files=sidecar_path, name='bids_events_bad'),
                     base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(isinstance(results, dict),
                            'process to short should return a dictionary when errors')
            self.assertEqual('warning', results['msg_category'], 'should give warning when JSON with errors')
            self.assertTrue(results['data'], 'should not convert using HED 8.2.0.xml')

    def test_sidecars_process_invalid_v2(self):
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/both_types_events_errors.json')
        arguments = {base_constants.SCHEMA: load_schema_version("8.2.0"),
                     base_constants.SIDECAR: Sidecar(files=sidecar_path, name='bids_events_bad'),
                     base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(isinstance(results, dict),
                            'process to short should return a dictionary when errors')
            self.assertEqual('warning', results['msg_category'], 'should give warning when JSON with errors')
            self.assertTrue(results['data'], 'should not convert using HED 8.2.0.xml')

    def test_sidecars_process_valid_to_short(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        arguments = {base_constants.SCHEMA: load_schema_version("8.2.0"),
                     base_constants.SIDECAR: Sidecar(files=json_path, name='bids_events'),
                     base_constants.EXPAND_DEFS: False,
                     base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}

        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(isinstance(results, dict),
                            'process to short should return a dict when no errors')
            self.assertEqual('success', results['msg_category'],
                             'process to short should return success if no errors')

    def test_sidecars_process_valid_to_short_defs_expanded(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        arguments = {base_constants.SCHEMA: load_schema_version("8.2.0"),
                     base_constants.SIDECAR: Sidecar(files=json_path, name='bids_events'),
                     base_constants.EXPAND_DEFS: True,
                     base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}

        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(isinstance(results, dict),
                            'process to short should return a dict when no errors and defs expanded')
            self.assertEqual('success', results['msg_category'],
                             'process to short should return success if no errors and defs_expanded')

    def test_sidecars_process_valid_to_long(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        arguments = {base_constants.SCHEMA: load_schema_version("8.2.0"),
                     base_constants.SIDECAR: Sidecar(files=json_path, name='bids_events'),
                     base_constants.EXPAND_DEFS: False,
                     base_constants.COMMAND: base_constants.COMMAND_TO_LONG}

        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(isinstance(results, dict),
                            'process to long should return a dict when no errors')
            self.assertEqual('success', results['msg_category'],
                             'process to long should return success when no errors')

    def test_sidecars_process_valid_to_long_defs_expanded(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        arguments = {base_constants.SCHEMA: load_schema_version("8.2.0"),
                     base_constants.SIDECAR: Sidecar(files=json_path, name='bids_events'),
                     base_constants.EXPAND_DEFS: False,
                     base_constants.COMMAND: base_constants.COMMAND_TO_LONG}
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.set_input_from_dict(arguments)
            results = proc_sidecars.process()
            self.assertTrue(isinstance(results, dict), 'should return a dict when no errors and defs expanded')
            self.assertEqual('success', results['msg_category'],
                             'should return success if converted when no errors and defs expanded')

    def test_sidecars_convert_to_long_invalid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.sidecar = Sidecar(files=json_path, name='bids_events_bad')
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_TO_LONG
            results = proc_sidecars.process()
            self.assertTrue(results['data'],
                            'sidecar_convert to long results should have data key')
            self.assertEqual('warning', results['msg_category'],
                             'sidecar_convert to long msg_category should be warning for errors')

    def test_sidecars_convert_to_long_valid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.sidecar = Sidecar(files=json_path, name='bids_events')
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_TO_LONG
            results = proc_sidecars.process()
            self.assertTrue(results['data'],
                            'sidecar_convert to long results should have data key')
            self.assertEqual('success', results["msg_category"],
                             'sidecar_convert to long msg_category should be success when no errors')

    def test_sidecars_convert_to_short_invalid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.sidecar = Sidecar(files=json_path, name='bids_events_bad')
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_TO_SHORT
            results = proc_sidecars.process()
            self.assertTrue(results['data'], 'sidecar_convert results should have data key')
            self.assertEqual('warning', results['msg_category'],
                             'sidecar_convert msg_category should be warning for errors')

    def test_bad_sidecar(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/both_types_events.json')
        json_sidecar = Sidecar(files=json_path, name='bids_events_bad')
        hed_schema = load_schema_version('8.2.0')
        issues = json_sidecar.validate(hed_schema)
        self.assertIsInstance(issues, list)
        self.assertEqual(len(issues), 37)

    def test_sidecars_convert_to_short_valid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.sidecar = Sidecar(files=json_path, name='bids_events')
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_TO_SHORT
            results = proc_sidecars.process()
            self.assertTrue(results['data'], 'sidecar_convert results should have data key')
            self.assertEqual('success', results['msg_category'],
                             'sidecar_convert msg_category should be success when no errors')

    def test_sidecars_validate_invalid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.sidecar = Sidecar(files=json_path, name='bids_events_bad')
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_VALIDATE
            results = proc_sidecars.process()
            self.assertTrue(results['data'],
                            'sidecar_validate results should have a data key when validation issues')
            self.assertEqual('warning', results['msg_category'],
                             'sidecar_validate msg_category should be warning when errors')

    def test_sidecars_validate_invalid_multiple(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.sidecar = Sidecar(files=json_path, name='bids_events_bad')
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_VALIDATE
            results = proc_sidecars.process()
            self.assertTrue(results['data'],
                            'sidecar_validate results should have a data key when validation issues')
            self.assertEqual('warning', results['msg_category'],
                             'sidecar_validate msg_category should be warning when errors')

    def test_sidecars_validate_valid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        with self.app.app_context():
            proc_sidecars = ProcessSidecars()
            proc_sidecars.sidecar = Sidecar(files=json_path, name='bids_events')
            proc_sidecars.schema = load_schema_version("8.2.0")
            proc_sidecars.command = base_constants.COMMAND_VALIDATE
            results = proc_sidecars.process()
            self.assertFalse(results['data'],
                             'sidecar_validate results should not have a data key when no validation issues')
            self.assertEqual('success', results["msg_category"],
                             'sidecar_validate msg_category should be success when no issues')


if __name__ == '__main__':
    unittest.main()
