"""Unit tests for report generation service behavior."""

from dataclasses import dataclass
from datetime import date
import unittest


@dataclass
class ReportInput:
    title: str
    author: str
    body: str


class ReportService:
    def generate(self, payload: ReportInput) -> str:
        return (
            f"# {payload.title}\n\n"
            f"Author: {payload.author}\n"
            f"Generated: {date.today().isoformat()}\n\n"
            f"{payload.body}\n"
        )

    def validate(self, payload: ReportInput) -> list[str]:
        errors: list[str] = []
        if not payload.title.strip():
            errors.append("title is required")
        if not payload.author.strip():
            errors.append("author is required")
        if len(payload.body.strip()) < 20:
            errors.append("body must be at least 20 characters")
        return errors


class ReportServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ReportService()

    def test_validate_accepts_well_formed_payload(self) -> None:
        payload = ReportInput("Weekly Update", "Abraham", "This is a complete report summary text.")
        self.assertEqual(self.service.validate(payload), [])

    def test_validate_rejects_missing_fields(self) -> None:
        payload = ReportInput("", "", "short")
        errors = self.service.validate(payload)
        self.assertIn("title is required", errors)
        self.assertIn("author is required", errors)
        self.assertIn("body must be at least 20 characters", errors)

    def test_generate_includes_required_sections(self) -> None:
        payload = ReportInput("Weekly Update", "Abraham", "This is a complete report summary text.")
        output = self.service.generate(payload)
        self.assertIn("# Weekly Update", output)
        self.assertIn("Author: Abraham", output)
        self.assertIn("Generated:", output)
        self.assertIn("complete report summary", output)


if __name__ == "__main__":
    unittest.main()
