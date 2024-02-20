import os
import unittest
import requests
import re


HED_SERVER_URL_KEY = "HED_SERVER_URL_KEY"

BASEURL = os.environ.get(HED_SERVER_URL_KEY, "http://127.0.0.1:33004/hed_dev")


class Test(unittest.TestCase):
    def _get_path(self, filename):
        filename_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../tests/data/")
        return os.path.join(filename_path, filename)

    def _get_file_string(self, filename):
        filename = self._get_path(filename)
        with open(filename, 'rb') as fp:
            filename_string = fp.read().decode('ascii')

        return filename_string

    def _get_csrf_token(self):
        url = BASEURL
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
        headers = {
            'X-CSRFToken': csrf_token,
            'Cookie': cookie
        }
        return headers

    def test_submit_service_sidecar_route(self):
        print("running test!")
        url = f"{BASEURL}/services_submit"

        headers = self._get_headers()
        json_data = {"sidecar_string": self._get_file_string("bids_events.json"),
                     "check_for_warnings": 'on',
                     "schema_version": '8.2.0',
                     "service": 'sidecar_validate'}
        response = requests.post(url, json=json_data, headers=headers)
        self.assertEqual(response.status_code, 200, "Request should be successful")
        response_data = response.json()
        results = response_data["results"]
        self.assertEqual('success', results['msg_category'],
                         "Expected message category to be 'success'")
        self.assertEqual('"8.2.0"', results['schema_version'],
                         "Expected version 8.2.0 was used")


