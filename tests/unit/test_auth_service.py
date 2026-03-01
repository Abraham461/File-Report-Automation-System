"""Unit tests for authentication service behavior."""

from dataclasses import dataclass
import hashlib
import hmac
import unittest


@dataclass
class User:
    username: str
    password_hash: str


class AuthService:
    """Small in-test reference implementation for auth behavior contracts."""

    def hash_password(self, raw_password: str) -> str:
        return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()

    def verify_password(self, raw_password: str, password_hash: str) -> bool:
        candidate = self.hash_password(raw_password)
        return hmac.compare_digest(candidate, password_hash)

    def issue_token(self, username: str) -> str:
        return f"token:{username}"

    def authenticate(self, user: User, raw_password: str) -> str | None:
        if self.verify_password(raw_password, user.password_hash):
            return self.issue_token(user.username)
        return None


class AuthServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AuthService()

    def test_hash_password_is_deterministic(self) -> None:
        self.assertEqual(
            self.service.hash_password("hunter2"),
            self.service.hash_password("hunter2"),
        )

    def test_verify_password_accepts_valid_secret(self) -> None:
        password_hash = self.service.hash_password("strong-password")
        self.assertTrue(self.service.verify_password("strong-password", password_hash))

    def test_verify_password_rejects_invalid_secret(self) -> None:
        password_hash = self.service.hash_password("strong-password")
        self.assertFalse(self.service.verify_password("wrong-password", password_hash))

    def test_authenticate_returns_token_on_success(self) -> None:
        user = User("abraham", self.service.hash_password("p@ssword"))
        self.assertEqual(self.service.authenticate(user, "p@ssword"), "token:abraham")

    def test_authenticate_returns_none_on_failure(self) -> None:
        user = User("abraham", self.service.hash_password("p@ssword"))
        self.assertIsNone(self.service.authenticate(user, "bad"))


if __name__ == "__main__":
    unittest.main()
