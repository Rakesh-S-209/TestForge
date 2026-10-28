"""Authentication service — DEMO ONLY.

Uses bcrypt password hashing and JWT tokens for demonstration purposes.
Do not use these tokens or this secret key in any real application without
replacing the secret key, adding proper key rotation, and enabling HTTPS.
"""

from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.repositories.user_repo import UserRepository

settings = get_settings()


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT with the given subject claim."""
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> str:
    """Decode a JWT and return the subject, or raise ValueError on failure."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise ValueError("Token missing 'sub' claim")
        return sub
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc


class AuthService:
    """Handles user registration and authentication."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def register(self, username: str, email: str, password: str) -> User:
        """Create a new demo user.  Raises ValueError on duplicate username/email."""
        if await self._repo.get_by_username(username):
            raise ValueError(f"Username '{username}' is already taken")
        if await self._repo.get_by_email(email):
            raise ValueError(f"Email '{email}' is already registered")
        hashed = hash_password(password)
        return await self._repo.create(username=username, email=email, hashed_password=hashed)

    async def authenticate(self, username: str, password: str) -> User:
        """Return the User if credentials are valid, else raise ValueError."""
        user = await self._repo.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid username or password")
        if not user.is_active:
            raise ValueError("Account is disabled")
        return user

    async def get_current_user(self, token: str) -> User:
        """Validate a JWT and return the corresponding User."""
        username = decode_token(token)
        user = await self._repo.get_by_username(username)
        if user is None:
            raise ValueError("User not found")
        return user
