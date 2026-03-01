"""Integration tests for canonical search API contract.

These tests run against a deployed FRAS instance when FRAS_BASE_URL is set.
"""

import json
import os
import unittest
from urllib import error, parse, request


class SearchApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = os.getenv("FRAS_BASE_URL")
        if not cls.base_url:
            raise unittest.SkipTest("Set FRAS_BASE_URL to run integration tests")

    def test_search_with_query_returns_results_payload(self) -> None:
        query = parse.urlencode({"q": "report"})
        req = request.Request(f"{self.base_url}/api/search?{query}", method="GET")
        with request.urlopen(req, timeout=10) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("query", data)
            self.assertIn("results", data)

    def test_search_requires_q_query_param(self) -> None:
        req = request.Request(f"{self.base_url}/api/search", method="GET")
        with self.assertRaises(error.HTTPError) as ctx:
            request.urlopen(req, timeout=10)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
