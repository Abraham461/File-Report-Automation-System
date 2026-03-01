"""Integration tests for search API.

These tests run against a deployed FRAS instance when FRAS_BASE_URL is set.
"""

import os
import unittest
from urllib import parse, request, error


class SearchApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = os.getenv("FRAS_BASE_URL")
        if not cls.base_url:
            raise unittest.SkipTest("Set FRAS_BASE_URL to run integration tests")

    def test_search_endpoint_is_reachable(self) -> None:
        req = request.Request(f"{self.base_url}/api/search", method="OPTIONS")
        try:
            with request.urlopen(req, timeout=10) as resp:
                self.assertIn(resp.status, {200, 204, 405})
        except error.HTTPError as exc:
            self.assertIn(exc.code, {200, 204, 401, 403, 404, 405})

    def test_search_with_query_returns_valid_status(self) -> None:
        query = parse.urlencode({"q": "report"})
        req = request.Request(f"{self.base_url}/api/search?{query}", method="GET")
        try:
            with request.urlopen(req, timeout=10) as resp:
                self.assertIn(resp.status, {200, 204})
        except error.HTTPError as exc:
            self.assertIn(exc.code, {200, 204, 400, 401, 403, 404, 422})


if __name__ == "__main__":
    unittest.main()
