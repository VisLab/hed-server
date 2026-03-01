import requests

from service_tests.test_service_base import ServicesTest


class TestEventServices(ServicesTest):
    def test_get_services(self):
        url = f"{self.BASEURL}/services_submit"
        json_data = {"service": "get_services"}
        response = requests.post(url, json=json_data, headers=self._get_headers())
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        print(
            f"Error report: [{response_data.get('error_type')}] {response_data.get('error_msg')}"
        )

        # Print out the results if available
        if "results" in response_data and response_data["results"]:
            results = response_data["results"]
            print(
                f"[{response_data.get('service')}] status {results.get('msg_category')}: {results.get('msg')}"
            )
            print(f"Return data:\n{results.get('data')}")

        self.assertFalse(response_data.get("error_type"))
        self.assertEqual(response_data["results"]["msg_category"], "success")
