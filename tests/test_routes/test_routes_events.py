import unittest

from flask import Response

from hedweb.constants import base_constants as bc
from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_events_results_empty_data(self):
        response = self.app.test.post('/events_submit')
        self.assertEqual(200, response.status_code, 'HED events request succeeds even when no data')
        self.assertTrue(isinstance(response, Response),
                        'events_results validate should return a response object when empty events')
        header_dict = dict(response.headers)
        self.assertEqual("error", header_dict["Category"], "The header msg_category when no events is error ")
        self.assertFalse(response.data, "The response data for empty events request is empty")

    def test_events_results_assemble_valid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_ASSEMBLE,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.EVENTS_FILE: self._get_file_buffer("bids_events.tsv"),
                          bc.EXPAND_DEFS: 'on',
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Assembly of a valid events file has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid events file should assemble successfully")
            self.assertTrue(response.data, "The assembled events file should not be empty")

    def test_events_results_assemble_invalid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_ASSEMBLE,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events_bad.json"),
                          bc.EVENTS_FILE: self._get_file_buffer("bids_events.tsv"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Assembly of invalid events files has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "Assembly with invalid events files generates a warning")
            self.assertTrue(response.data,
                            "The response data for invalid event assembly should have error messages")

    def test_events_results_quality_checker_invalid(self):
        data = ''
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.3.0',
                          bc.COMMAND_OPTION: bc.COMMAND_CHECK_QUALITY,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.EVENTS_FILE: self._get_file_buffer("bids_events.tsv"),
                          bc.LIMIT_ERRORS: 'on',
                          bc.SHOW_DETAILS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Check quality of file has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "The events file should have quality issues")
            self.assertTrue(response.data, "The quality checker should have data.")
            data = response.data

        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.3.0',
                          bc.COMMAND_OPTION: bc.COMMAND_CHECK_QUALITY,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.EVENTS_FILE: self._get_file_buffer("bids_events.tsv"),
                          bc.LIMIT_ERRORS: 'off',
                          bc.SHOW_DETAILS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Check quality of file has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "The events file should have quality issues")
            self.assertTrue(response.data, "The quality checker should have data.")
        self.assertGreater(len(response.data), len(data),
                           "The quality checker should have more data when limit_errors is off")

    def test_events_results_remodel_valid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_REMODEL,
                          bc.REMODEL_FILE: self._get_file_buffer('simple_reorder_rmdl.json'),
                          bc.EVENTS_FILE: self._get_file_buffer("sub-002_task-FacePerception_run-1_events.tsv")}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit remodel should return a Response when commands are valid')
            self.assertEqual(200, response.status_code, 'Remodeling valid file has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "A valid remodeling operation should be successful")
            self.assertTrue(response.data, "The remodeled events file should return data")

    def test_events_results_remodel_summary(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_REMODEL,
                          bc.INCLUDE_SUMMARIES: 'on',
                          bc.REMODEL_FILE: self._get_file_buffer('test_with_summary_rmdl.json'),
                          bc.EVENTS_FILE: self._get_file_buffer("sub-002_task-FacePerception_run-1_events.tsv")}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit remodel should return a Response when commands are valid')
            self.assertEqual(200, response.status_code, 'Remodeling valid file has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "A valid remodeling operation should be successful")
            self.assertTrue(response.data, "The remodeled events file should return data")

    def test_events_results_remodel_invalid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_REMODEL,
                          bc.REMODEL_FILE: self._get_file_buffer('bad_reorder_remdl.json'),
                          bc.EVENTS_FILE: self._get_file_buffer("sub-002_task-FacePerception_run-1_events.tsv")}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit remodel should return a Response when commands are valid')
            self.assertEqual(200, response.status_code, 'Remodeling valid file has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "An invalid remodeling operation should result in warning")
            self.assertTrue(response.data, "The invalid commands should return data")

    def test_events_results_validate_valid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.EVENTS_FILE: self._get_file_buffer("bids_events.tsv"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit validate should return a Response when events valid')
            self.assertEqual(200, response.status_code, 'Validation of a valid events file has a valid status code')
            headers_dict = dict(response.headers)
            self.assertEqual("success", headers_dict["Category"],
                             "The valid events file should validate successfully")
            self.assertFalse(response.data, "The validated events file should not return data")

    def test_events_results_validate_invalid(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_VALIDATE,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events_bad.json"),
                          bc.EVENTS_FILE: self._get_file_buffer("bids_events.tsv"),
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertTrue(isinstance(response, Response),
                            'events_submit validate should return a Response when events invalid')
            self.assertEqual(200, response.status_code, 'Validation of invalid events files has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("warning", headers_dict["Category"],
                             "Validation of invalid events files generates a warning")
            self.assertTrue(response.data,
                            "The response data for invalid event validation should have error messages")

    def test_events_results_validate_bad_file(self):
        with self.app.app_context():
            input_data = {bc.SCHEMA_VERSION: '8.2.0',
                          bc.COMMAND_OPTION: bc.COMMAND_ASSEMBLE,
                          bc.SIDECAR_FILE: self._get_file_buffer("bids_events.json"),
                          bc.EVENTS_FILE: self._get_file_buffer("bids_events.json"),
                          bc.EXPAND_DEFS: 'on',
                          bc.CHECK_FOR_WARNINGS: 'on'}
            response = self.app.test.post('/events_submit', content_type='multipart/form-data', data=input_data)
            self.assertEqual(200, response.status_code, 'Invalid events file has a response')
            headers_dict = dict(response.headers)
            self.assertEqual("error", headers_dict["Category"], "The invalid events file not validate")
            self.assertTrue(headers_dict["Message"].startswith("INVALID_FILE_FORMAT"))
            self.assertFalse(response.data, "The assembled events file should be empty")


if __name__ == '__main__':
    unittest.main()
