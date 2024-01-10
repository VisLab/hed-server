import io
import os
import unittest
from flask import Response
from tests.test_web_base import TestWebBase
from hedweb.constants import base_constants


class Test(TestWebBase):

    def test_events_results_empty_data(self):
        response = self.app.test.post('/events_submit')
        self.assertEqual(200, response.status_code, 'HED events request succeeds even when no data')
        self.assertTrue(isinstance(response, Response),
                        'events_results validate should return a response object when empty events')
        header_dict = dict(response.headers)
        self.assertEqual("error", header_dict["Category"], "The header msg_category when no events is error ")
        self.assertFalse(response.data, "The response data for empty events request is empty")

    def test_events_results_assemble_valid(self):
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.json')
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.tsv')

        with open(sidecar_path, 'r') as sc:
            x = sc.read()
        sidecar_buffer = io.BytesIO(bytes(x, 'utf-8'))

        with open(events_path, 'r') as sc:
            y = sc.read()
        events_buffer = io.BytesIO(bytes(y, 'utf-8'))

        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.2.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_ASSEMBLE,
                          'sidecar_file': (sidecar_buffer, 'bids_events.json'),
                          'events_file': (events_buffer, 'bids_events.tsv'),
                          'expand_defs': 'on',
                          base_constants.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Assembly of a valid events file has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid events file should assemble successfully")
            self.assertTrue(response.data, "The assembled events file should not be empty")
            sidecar_buffer.close()
            events_buffer.close()

    def test_events_results_assemble_invalid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events_bad.json')
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.tsv')

        with open(json_path, 'r') as sc:
            x = sc.read()
        json_buffer = io.BytesIO(bytes(x, 'utf-8'))

        with open(events_path, 'r') as sc:
            y = sc.read()
        events_buffer = io.BytesIO(bytes(y, 'utf-8'))

        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.2.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_ASSEMBLE,
                          base_constants.SIDECAR_FILE: (json_buffer, 'bids_events_bad.json'),
                          base_constants.EVENTS_FILE: (events_buffer, 'bids_events.tsv'),
                          base_constants.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Assembly of invalid events files has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "Assembly with invalid events files generates a warning")
            self.assertTrue(response.data,
                            "The response data for invalid event assembly should have error messages")
            json_buffer.close()

    def test_events_results_remodel_valid(self):
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '../data/sub-002_task-FacePerception_run-1_events.tsv')
        remodel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../data/simple_reorder_rmdl.json')
        with open(events_path, 'r') as sc:
            y = sc.read()
        events_buffer = io.BytesIO(bytes(y, 'utf-8'))

        with open(remodel_path, 'r') as sc:
            x = sc.read()
        remodel_buffer = io.BytesIO(bytes(x, 'utf-8'))

        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.2.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_REMODEL,
                          base_constants.REMODEL_FILE: (remodel_buffer, 'simple_reorder_rmdl.json'),
                          base_constants.EVENTS_FILE: (events_buffer,
                                                       'sub-002_task-FacePerception_run-1_events.tsv.tsv')}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit remodel should return a Response when commands are valid')
            self.assertEqual(200, response.status_code, 'Remodeling valid file has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "A valid remodeling operation should be successful")
            self.assertTrue(response.data, "The remodeled events file should return data")
            remodel_buffer.close()
            events_buffer.close()

    def test_events_results_remodel_invalid(self):
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '../data/sub-002_task-FacePerception_run-1_events.tsv')
        remodel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../data/bad_reorder_remdl.json')
        with open(events_path, 'r') as sc:
            y = sc.read()
        events_buffer = io.BytesIO(bytes(y, 'utf-8'))

        with open(remodel_path, 'r') as sc:
            x = sc.read()
        remodel_buffer = io.BytesIO(bytes(x, 'utf-8'))

        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.2.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_REMODEL,
                          base_constants.REMODEL_FILE: (remodel_buffer, 'bad_reorder_remdl.json'),
                          base_constants.EVENTS_FILE: (events_buffer,
                                                       'sub-002_task-FacePerception_run-1_events.tsv')}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit remodel should return a Response when commands are valid')
            self.assertEqual(200, response.status_code, 'Remodeling valid file has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "An invalid remodeling operation should result in warning")
            self.assertTrue(response.data, "The invalid commands should return data")
            remodel_buffer.close()
            events_buffer.close()

    def test_events_results_validate_valid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.json')
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.tsv')

        with open(json_path, 'r') as sc:
            x = sc.read()
        json_buffer = io.BytesIO(bytes(x, 'utf-8'))

        with open(events_path, 'r') as sc:
            y = sc.read()
        events_buffer = io.BytesIO(bytes(y, 'utf-8'))

        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.2.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_VALIDATE,
                          base_constants.SIDECAR_FILE: (json_buffer, 'bids_events.json'),
                          base_constants.EVENTS_FILE: (events_buffer, 'bids_events.tsv'),
                          base_constants.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit validate should return a Response when events valid')
            self.assertEqual(200, response.status_code, 'Validation of a valid events file has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid events file should validate successfully")
            self.assertFalse(response.data, "The validated events file should not return data")
            json_buffer.close()
            events_buffer.close()

    def test_events_results_validate_invalid(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events_bad.json')
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.tsv')

        with open(json_path, 'r') as sc:
            x = sc.read()
        json_buffer = io.BytesIO(bytes(x, 'utf-8'))

        with open(events_path, 'r') as sc:
            y = sc.read()
        events_buffer = io.BytesIO(bytes(y, 'utf-8'))

        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.2.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_VALIDATE,
                          base_constants.SIDECAR_FILE: (json_buffer, 'bids_events_bad.json'),
                          base_constants.EVENTS_FILE: (events_buffer, 'events_file'),
                          base_constants.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit validate should return a Response when events invalid')
            self.assertEqual(200, response.status_code, 'Validation of invalid events files has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "Validation of invalid events files generates a warning")
            self.assertTrue(response.data,
                            "The response data for invalid event validation should have error messages")
            json_buffer.close()
            events_buffer.close()

    def test_events_results_validate_bad_file(self):
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.json')
        with open(sidecar_path, 'r') as sc:
            x = sc.read()
        sidecar_buffer = io.BytesIO(bytes(x, 'utf-8'))

        with self.app.app_context():
            input_data = {base_constants.SCHEMA_VERSION: '8.2.0',
                          base_constants.COMMAND_OPTION: base_constants.COMMAND_ASSEMBLE,
                          'sidecar_file': (sidecar_buffer, 'bids_events.json'),
                          'events_file': (sidecar_buffer, 'bids_events.tsv'),
                          'expand_defs': 'on',
                          base_constants.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Invalid events file has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("error", headers_dict["Category"], "The invalid events file not validate")
            self.assertTrue(headers_dict["Message"].startswith("INVALID_FILE_FORMAT"))
            self.assertFalse(response.data, "The assembled events file should be empty")
            sidecar_buffer.close()


if __name__ == '__main__':
    unittest.main()
