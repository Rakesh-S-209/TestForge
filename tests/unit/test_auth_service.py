"""Unit tests for authentication service functions.

Test IDs: AUTH-UNIT-001 through AUTH-UNIT-010
"""

import pytest

from app.services.auth_service import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)

# ---------------------------------------------------------------------------
# AUTH-UNIT-001 to 003 — Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    """AUTH-UNIT-001 to AUTH-UNIT-003: bcrypt hash and verify functions."""

    def test_hash_returns_non_empty_string(self):
        """AUTH-UNIT-001: hash_password must return a non-empty string."""
        hashed = hash_password("mypassword")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_is_not_plaintext(self):
        """AUTH-UNIT-002: The hash must not equal the original password."""
        plain = "mypassword"
        hashed = hash_password(plain)
        assert hashed != plain

    def test_verify_correct_password(self):
        """AUTH-UNIT-003: verify_password returns True for matching password."""
        plain = "correct-horse-battery-staple"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        """AUTH-UNIT-004: verify_password returns False for wrong password."""
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        """AUTH-UNIT-005: bcrypt generates a unique salt each time (no rainbow tables)."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # different salts


# ---------------------------------------------------------------------------
# AUTH-UNIT-006 to 010 — JWT token creation and decoding
# ---------------------------------------------------------------------------

class TestJWTTokens:
    """AUTH-UNIT-006 to AUTH-UNIT-010: JWT create/decode."""

    def test_create_and_decode_token(self):
        """AUTH-UNIT-006: A token created for a subject decodes to that subject."""
        token = create_access_token("alice")
        assert decode_token(token) == "alice"

    def test_tampered_token_raises_value_error(self):
        """AUTH-UNIT-007: A modified token must raise ValueError, not crash silently."""
        token = create_access_token("alice")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token(tampered)

    def test_empty_token_raises_value_error(self):
        """AUTH-UNIT-008: An empty string token raises ValueError."""
        with pytest.raises(ValueError):
            decode_token("")

    def test_random_string_raises_value_error(self):
        """AUTH-UNIT-009: A random string that looks nothing like a JWT raises ValueError."""
        with pytest.raises(ValueError):
            decode_token("not.a.token")

    def test_token_subject_preserved_for_various_usernames(self):
        """AUTH-UNIT-010: Parametrize over several username strings."""
        for username in ["alice", "bob_99", "user@domain", "中文用户"]:
            token = create_access_token(username)
            assert decode_token(token) == username
