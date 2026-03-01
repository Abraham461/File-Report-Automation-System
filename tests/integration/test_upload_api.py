"""Integration tests for canonical upload API contract.

These tests run against a deployed FRAS instance when FRAS_BASE_URL is set.
"""

import json
import os
import unittest
from urllib import error, request


class UploadApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = os.getenv("FRAS_BASE_URL")
        if not cls.base_url:
            raise unittest.SkipTest("Set FRAS_BASE_URL to run integration tests")

    def test_upload_endpoint_accepts_non_empty_files_payload(self) -> None:
        payload = json.dumps({"files": [{"name": "contract-001.pdf"}]}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/upload",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req, timeout=10) as resp:
            self.assertEqual(resp.status, 201)

    def test_upload_endpoint_rejects_empty_payload(self) -> None:
        payload = json.dumps({"files": []}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/upload",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(error.HTTPError) as ctx:
            request.urlopen(req, timeout=10)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
