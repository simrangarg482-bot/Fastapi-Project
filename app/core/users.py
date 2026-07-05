"""
Minimal user store.

This is intentionally still in-memory (no database in this project yet),
but it replaces the hardcoded `admin/admin` check with:
  - multiple possible users
  - hashed passwords instead of plaintext comparison

Swap `_USERS` for a real table (e.g. a `users` model + DB session) when
you add persistence -- the `authenticate_user` function is the only
thing the rest of the app depends on, so that's the one seam to change.
"""
import os
import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash(password: str) -> str:
    """
    bcrypt has a hard 72-byte limit and raises ValueError above that.
    Pre-hashing with SHA-256 first normalizes any input to a fixed-length
    hex string (64 chars), so passwords of any length are safe to use.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _hash(password: str) -> str:
    return pwd_context.hash(_prehash(password))


def _verify(password: str, hashed: str) -> bool:
    return pwd_context.verify(_prehash(password), hashed)


# Seed user(s). Password comes from an env var so it's never plaintext
# in source control; falls back to a random-ish dev password if unset,
# so local dev still works without needing to set anything.
_DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "author")
_DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "pass")

_USERS = {
    _DEFAULT_ADMIN_USERNAME: {
        "username": _DEFAULT_ADMIN_USERNAME,
        "hashed_password": _hash(_DEFAULT_ADMIN_PASSWORD),
    }
}


def authenticate_user(username: str, password: str) -> dict | None:
    """Return the user dict if credentials are valid, else None."""
    user = _USERS.get(username)
    if not user:
        return None
    if not _verify(password, user["hashed_password"]):
        return None
    return user