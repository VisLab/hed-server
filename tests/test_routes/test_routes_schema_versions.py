import json
import unittest
from unittest.mock import patch

from tests.test_routes.test_routes_base import TestRouteBase


class Test(TestRouteBase):
    def test_schema_versions(self):
        with self.app.app_context():
            response = self.app.test.get("/schema_versions")
            self.assertEqual(200, response.status_code, "The HED version list does not require data")
            versions = response.data
            self.assertTrue(versions, "The returned data is not empty")
            v_dict = json.loads(versions)
            self.assertIsInstance(v_dict, dict, "The versions are returned in a dictionary")
            v_list = v_dict["schema_version_list"]
            self.assertIsInstance(v_list, list, "The versions are in a list")

    def test_schema_versions_without_prereleases(self):
        """Test schema_versions endpoint without include_prereleases parameter."""
        with self.app.app_context():
            response = self.app.test.get("/schema_versions")
            self.assertEqual(200, response.status_code)
            v_dict = json.loads(response.data)
            v_list = v_dict["schema_version_list"]
            # Check that no prerelease versions are included
            for version in v_list:
                self.assertNotIn(
                    "(prerelease)",
                    version,
                    "Should not include prerelease versions by default",
                )

    def test_schema_versions_with_prereleases_false(self):
        """Test schema_versions endpoint with include_prereleases=false."""
        with self.app.app_context():
            response = self.app.test.get("/schema_versions?include_prereleases=false")
            self.assertEqual(200, response.status_code)
            v_dict = json.loads(response.data)
            v_list = v_dict["schema_version_list"]
            # Check that no prerelease versions are included
            for version in v_list:
                self.assertNotIn(
                    "(prerelease)",
                    version,
                    "Should not include prerelease versions when false",
                )

    def test_schema_versions_with_prereleases_true(self):
        """Test schema_versions endpoint with include_prereleases=true."""
        with self.app.app_context():
            response = self.app.test.get("/schema_versions?include_prereleases=true")
            self.assertEqual(200, response.status_code)
            v_dict = json.loads(response.data)
            v_list = v_dict["schema_version_list"]
            self.assertIsInstance(v_list, list, "Should return a list of versions")
            # The list should include all versions (stable + prerelease if any exist)
            # We can't assert that prereleases exist, but the endpoint should work

    def test_schema_versions_fallback_succeeds(self):
        """Test successful fallback when online and local sources are empty."""
        with self.app.app_context():
            with (
                patch("hedweb.routes.hedschema.get_available_hed_versions") as mock_available,
                patch("hedweb.routes.hedschema.get_hed_versions") as mock_local,
            ):
                mock_available.return_value = {}

                def mock_get_hed_versions_impl(**kwargs):
                    if "local_hed_directory" in kwargs:
                        # Fallback succeeds and returns versions (dict with library_name: [versions])
                        return {None: ["8.3.0", "8.2.0"]}
                    # Normal calls return empty
                    return {}

                mock_local.side_effect = mock_get_hed_versions_impl

                response = self.app.test.get("/schema_versions")
                self.assertEqual(200, response.status_code)
                v_dict = json.loads(response.data)
                v_list = v_dict["schema_version_list"]
                # Verify fallback actually recovered versions from installed cache
                self.assertTrue(len(v_list) > 0, "Fallback should have recovered versions from installed cache")
                self.assertIn("8.3.0", v_list, "Should contain 8.3.0 from fallback")
                self.assertIn("8.2.0", v_list, "Should contain 8.2.0 from fallback")

    def test_schema_versions_fallback_to_installed_cache(self):
        """Test schema_versions endpoint fallback does not crash when both sources fail."""
        with self.app.app_context():
            with (
                patch("hedweb.routes.hedschema.get_available_hed_versions") as mock_available,
                patch("hedweb.routes.hedschema.get_hed_versions") as mock_local,
            ):
                # Both sources fail—online returns empty, local returns empty
                mock_available.return_value = {}

                # Setup get_hed_versions to return empty for normal calls,
                # then fail on fallback to simulate an exception scenario
                def mock_get_hed_versions_impl(**kwargs):
                    if "local_hed_directory" in kwargs:
                        # Fallback call fails with an exception
                        raise Exception("Simulated fallback failure")
                    # Normal calls return empty
                    return {}

                mock_local.side_effect = mock_get_hed_versions_impl

                # Even with a fallback exception, the endpoint should still return 200
                # and handle the error gracefully
                response = self.app.test.get("/schema_versions")
                self.assertEqual(200, response.status_code, "Should return 200 even with fallback exception")
                v_dict = json.loads(response.data)
                # Should have error info or empty list, but not crash
                self.assertIn("schema_version_list", v_dict, "Response should have schema_version_list key")

    def test_schema_versions_fallback_with_missing_get_cache_directory(self):
        """Test fallback handles missing get_cache_directory() in older hedtools versions."""
        with self.app.app_context():
            with (
                patch("hedweb.routes.hedschema.get_available_hed_versions") as mock_available,
                patch("hedweb.routes.hedschema.get_hed_versions") as mock_local,
                patch(
                    "hedweb.routes.hedschema.get_cache_directory",
                    side_effect=AttributeError("get_cache_directory not found"),
                ) as mock_cache_dir,
            ):
                # Both sources fail—online returns empty, local returns empty
                mock_available.return_value = {}

                # Setup get_hed_versions to handle fallback call
                def mock_get_hed_versions_impl(**kwargs):
                    if "local_hed_directory" in kwargs:
                        # Fallback call with installed cache
                        return {"8.3.0": {}, "8.2.0": {}}
                    # Normal calls return empty
                    return {}

                mock_local.side_effect = mock_get_hed_versions_impl

                # The endpoint should handle the missing get_cache_directory gracefully
                # and still call the fallback recovery
                response = self.app.test.get("/schema_versions")
                self.assertEqual(200, response.status_code, "Should return 200 despite missing get_cache_directory")
                v_dict = json.loads(response.data)
                self.assertIn("schema_version_list", v_dict, "Response should have schema_version_list key")
                # Verify that the endpoint did not crash and the fallback was attempted
                # (the mock_cache_dir.side_effect will have been called and caught)
                self.assertTrue(mock_cache_dir.called, "get_cache_directory() should have been called")


if __name__ == "__main__":
    unittest.main()
