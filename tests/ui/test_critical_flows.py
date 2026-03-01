"""Basic UI flow checks for FRAS critical pages.

Set FRAS_BASE_URL to run these against a deployed environment.
"""

import os
import unittest
from urllib import request


class CriticalUiFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = os.getenv("FRAS_BASE_URL")
        if not cls.base_url:
            raise unittest.SkipTest("Set FRAS_BASE_URL to run UI tests")

    def _fetch_page(self, route: str) -> str:
        with request.urlopen(f"{self.base_url}{route}", timeout=10) as response:
            self.assertEqual(response.status, 200)
            return response.read().decode("utf-8", errors="ignore").lower()

    def test_login_flow_page_loads(self) -> None:
        html = self._fetch_page("/login")
        self.assertIn("login", html)

    def test_upload_flow_page_loads(self) -> None:
        html = self._fetch_page("/upload")
        self.assertTrue("upload" in html or "file" in html)

    def test_search_flow_page_loads(self) -> None:
        html = self._fetch_page("/search")
        self.assertIn("search", html)

    def test_generate_report_flow_page_loads(self) -> None:
        html = self._fetch_page("/reports")
        self.assertTrue("report" in html or "generate" in html)


if __name__ == "__main__":
    unittest.main()
