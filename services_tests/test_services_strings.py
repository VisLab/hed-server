import requests

from services_tests.test_services_base import ServicesTest


class TestStringServices(ServicesTest):
    def test_validate_valid_hed_strings(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "strings_validate",
            "schema_version": "8.2.0",
            "string_list": self.data["goodStrings"],
            "check_for_warnings": True,
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get("error_type"))
        self.assertEqual(response_data["results"]["msg_category"], "success")

    def test_validate_invalid_hed_strings_with_url(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "strings_validate",
            "schema_url": "https://example.com/hed/schema",
            "string_list": self.data["badStrings"],
            "check_for_warnings": True,
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data.get("error_type"))

    def test_validate_invalid_hed_strings_with_schema(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "strings_validate",
            "schema_string": self.data["schemaText"],
            "string_list": self.data["badStrings"],
            "check_for_warnings": True,
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # Expecting a warning or error message, not a success
        self.assertNotEqual(response_data["results"]["msg_category"], "success")

    def test_convert_valid_strings_to_long(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "strings_to_long",
            "schema_version": "8.2.0",
            "string_list": self.data["goodStrings"],
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get("error_type"))
        self.assertEqual(response_data["results"]["msg_category"], "success")

    def test_validate_with_prereleases_false(self):
        """Test validation with include_prereleases=false."""
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "strings_validate",
            "schema_version": "8.2.0",
            "string_list": self.data["goodStrings"],
            "include_prereleases": "false",
            "check_for_warnings": True,
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get("error_type"))
        self.assertEqual(response_data["results"]["msg_category"], "success")

    def test_validate_with_prereleases_true(self):
        """Test validation with include_prereleases=true."""
        url = f"{self.BASEURL}/services_submit"
        json_data = {
            "service": "strings_validate",
            "schema_version": "8.2.0",
            "string_list": self.data["goodStrings"],
            "include_prereleases": "true",
            "check_for_warnings": True,
        }
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data.get("error_type"))
        self.assertEqual(response_data["results"]["msg_category"], "success")
