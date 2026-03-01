"""Integration tests for canonical report API contract.

These tests run against a deployed FRAS instance when FRAS_BASE_URL is set.
"""

import json
import os
import unittest
from urllib import error, request


class ReportApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = os.getenv("FRAS_BASE_URL")
        if not cls.base_url:
            raise unittest.SkipTest("Set FRAS_BASE_URL to run integration tests")

    def test_generate_report_canonical_endpoint_rejects_invalid_payload(self) -> None:
        payload = json.dumps({"title": "", "body": "short"}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/reports",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(error.HTTPError) as ctx:
            request.urlopen(req, timeout=10)
        self.assertEqual(ctx.exception.code, 400)

    def test_generate_report_compatibility_alias_matches_behavior(self) -> None:
        payload = json.dumps({"title": "", "body": "short"}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/reports/generate",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(error.HTTPError) as ctx:
            request.urlopen(req, timeout=10)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
