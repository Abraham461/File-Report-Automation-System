"""Integration tests for report API.

These tests run against a deployed FRAS instance when FRAS_BASE_URL is set.
"""

import json
import os
import unittest
from urllib import request, error


class ReportApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = os.getenv("FRAS_BASE_URL")
        if not cls.base_url:
            raise unittest.SkipTest("Set FRAS_BASE_URL to run integration tests")

    def test_report_endpoint_is_reachable(self) -> None:
        req = request.Request(f"{self.base_url}/api/reports", method="OPTIONS")
        try:
            with request.urlopen(req, timeout=10) as resp:
                self.assertIn(resp.status, {200, 204, 405})
        except error.HTTPError as exc:
            self.assertIn(exc.code, {200, 204, 401, 403, 404, 405})

    def test_generate_report_rejects_invalid_payload(self) -> None:
        payload = json.dumps({"title": "", "body": "short"}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/reports",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(error.HTTPError) as ctx:
            request.urlopen(req, timeout=10)
        self.assertIn(ctx.exception.code, {400, 401, 403, 415, 422})


if __name__ == "__main__":
    unittest.main()
