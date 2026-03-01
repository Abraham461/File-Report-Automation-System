import os
import tempfile
import threading
import time
import unittest
from urllib.request import urlopen
import json

import app


class SearchApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        app.DB_PATH = os.path.join(cls.tmp.name, "test.db")
        app.init_db()
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def test_keyword_search(self):
        payload = app.search_files({"q": ["finance"]})
        self.assertGreaterEqual(payload["total"], 1)

    def test_filters_and_sort(self):
        with urlopen(
            f"http://127.0.0.1:{self.port}/api/search?q=template&category=legal&sort=name"
        ) as resp:
            data = json.load(resp)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["results"][0]["category"], "legal")


if __name__ == "__main__":
    unittest.main()
