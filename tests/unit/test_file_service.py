"""Unit tests for file service behavior."""

from dataclasses import dataclass
import unittest


@dataclass
class StoredFile:
    file_id: str
    name: str
    content_type: str
    owner: str


class FileService:
    def __init__(self) -> None:
        self._files: dict[str, StoredFile] = {}

    def store(self, file: StoredFile) -> None:
        self._files[file.file_id] = file

    def find(self, file_id: str) -> StoredFile | None:
        return self._files.get(file_id)

    def search(self, query: str) -> list[StoredFile]:
        needle = query.lower().strip()
        return [f for f in self._files.values() if needle in f.name.lower()]

    def delete(self, file_id: str) -> bool:
        return self._files.pop(file_id, None) is not None


class FileServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FileService()
        self.service.store(StoredFile("f-1", "student-report.pdf", "application/pdf", "abraham"))
        self.service.store(StoredFile("f-2", "budget-sheet.xlsx", "application/vnd.ms-excel", "abraham"))

    def test_store_and_find_file(self) -> None:
        doc = self.service.find("f-1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.name, "student-report.pdf")

    def test_search_is_case_insensitive(self) -> None:
        result = self.service.search("REPORT")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].file_id, "f-1")

    def test_search_returns_empty_when_no_match(self) -> None:
        self.assertEqual(self.service.search("invoice"), [])

    def test_delete_existing_file(self) -> None:
        self.assertTrue(self.service.delete("f-2"))
        self.assertIsNone(self.service.find("f-2"))

    def test_delete_missing_file(self) -> None:
        self.assertFalse(self.service.delete("not-found"))


if __name__ == "__main__":
    unittest.main()
