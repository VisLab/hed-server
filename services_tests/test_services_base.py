import os
import re
import unittest

import requests

HED_SERVER_URL_ENV_KEYS = ["HED_SERVER_URL_KEY", "HED_SERVER_URL"]

# Determine BASEURL from either env var, default to local dev server
BASEURL = None
for _key in HED_SERVER_URL_ENV_KEYS:
    BASEURL = os.environ.get(_key)
    if BASEURL:
        break
if not BASEURL:
    BASEURL = "http://127.0.0.1:5000"


class ServicesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = cls.get_demo_data()
        cls.BASEURL = BASEURL

    @staticmethod
    def get_demo_data():
        data = {
            "descPrefix": "Property/Informational-property/Description/",
            "eventsText": "",
            "jsonBadText": "",
            "jsonText": "",
            "labelPrefix": "Property/Informational-property/Label/",
            "schemaUrl": "https://raw.githubusercontent.com/hed-standard/hed-schemas/master/standard_schema/hedxml/HED8.2.0.xml",
            "schemaText": "",
            "spreadsheetText": "",
            "spreadsheetTextInvalid": "",
            "remodelRemoveColumnsText": "",
            "remodelSummarizeColumnsText": "",
            "remodelSummarizeTypesText": "",
            "remodelFactorTypesText": "",
            "spreadsheetTextExtracted": "",
            "goodStrings": ["Red,Blue", "Green", "White, (Black, Image)"],
            "badStrings": ["Red, Blue, Blech", "Green", "White, Black, Binge"],
        }

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(cur_dir, "data")

        demo_path = os.path.join(data_path, "eeg_ds003645s_hed_demo")
        events_file = os.path.join(
            "sub-002",
            "ses-1",
            "eeg",
            "sub-002_ses-1_task-FacePerception_run-1_events.tsv",
        )

        # Reading files and assigning contents to the respective keys in the data dictionary
        with open(os.path.join(demo_path, "task-FacePerception_events.json")) as file:
            data["jsonText"] = file.read()

        with open(os.path.join(demo_path, events_file)) as file:
            data["eventsText"] = file.read()

        with open(os.path.join(data_path, "schema_data", "HED8.2.0.xml")) as file:
            data["schemaText"] = file.read()

        # Repeat the above pattern to read other files
        files_to_read = {
            "remodelRemoveColumnsText": "remove_extra_rmdl.json",
            "remodelSummarizeColumnsText": "summarize_columns_rmdl.json",
            "remodelSummarizeTypesText": "summarize_hed_types_rmdl.json",
            "remodelFactorTypesText": "factor_hed_types_rmdl.json",
            "jsonBadText": "both_types_events_errors.json",
            "spreadsheetText": "LKTEventCodesHED3.tsv",
            "spreadsheetTextExtracted": "task-FacePerception_events_extracted.tsv",
            "spreadsheetTextInvalid": "LKTEventCodesHED2.tsv",
        }

        for key, filename in files_to_read.items():
            file_path = os.path.join(data_path, "other_data", filename)
            with open(file_path) as file:
                data[key] = file.read()

        return data

    def _get_path(self, filename):
        filename_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../tests/data/"
        )
        return os.path.join(filename_path, filename)

    def _get_file_string(self, filename):
        filename = self._get_path(filename)
        with open(filename, "rb") as fp:
            filename_string = fp.read().decode("utf-8")

        return filename_string

    def _get_csrf_token(self):
        url = self.BASEURL
        response = requests.get(url)
        self.assertEqual(response.status_code, 200, "Get should be successful")
        header = response.headers
        cookie = header["Set-cookie"]
        csrf_token = re.search('let csrf_token = "(.*?)"', response.text)
        if not csrf_token:
            raise ValueError("No csrf token found on page")
        csrf_token = str(csrf_token.group(1))
        return cookie, csrf_token

    def _get_headers(self):
        cookie, csrf_token = self._get_csrf_token()
        headers = {"X-CSRFToken": csrf_token, "Cookie": cookie}
        return headers

    # def test_submit_service_sidecar_route(self):
    #     print("running test!")
    #     url = f"{BASEURL}/services_submit"
    #
    #     headers = self._get_headers()
    #     json_data = {"sidecar_string": self._get_file_string("bids_events.json"),
    #                  "check_for_warnings": 'on',
    #                  "schema_version": '8.2.0',
    #                  "service": 'sidecar_validate'}
    #     response = requests.post(url, json=json_data, headers=headers)
    #     self.assertEqual(response.status_code, 200, "Request should be successful")
    #     response_data = response.json()
    #     results = response_data["results"]
    #     self.assertEqual('success', results['msg_category'],
    #                      "Expected message category to be 'success'")
    #     self.assertEqual('"8.2.0"', results['schema_version'],
    #                      "Expected version 8.2.0 was used")

    # def test_submit_service_sidecar_route(self):
    #     url = f"{self.BASEURL}/services_submit"
    #
    #     headers = self._get_headers()
    #     json_data = {"sidecar_string": self._get_file_string("bids_events.json"),
    #                  "check_for_warnings": 'on',
    #                  "schema_version": '8.2.0',
    #                  "service": 'sidecar_validate'}
    #     response = requests.post(url, json=json_data, headers=headers)
    #     self.assertEqual(response.status_code, 200, "Request should be successful")
    #     response_data = response.json()
    #     results = response_data["results"]
    #     self.assertEqual('success', results['msg_category'],
    #                      "Expected message category to be 'success'")
    #     self.assertEqual('"8.2.0"', results['schema_version'],
    #                      "Expected version 8.2.0 was used")
