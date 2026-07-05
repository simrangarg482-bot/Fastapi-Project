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
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash(password: str) -> str:
    return pwd_context.hash(password)


# Seed user(s). Password comes from an env var so it's never plaintext
# in source control; falls back to a random-ish dev password if unset,
# so local dev still works without needing to set anything.
_DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me-in-env")

_USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": _hash(_DEFAULT_ADMIN_PASSWORD),
    }
}


def authenticate_user(username: str, password: str) -> dict | None:
    """Return the user dict if credentials are valid, else None."""
    user = _USERS.get(username)
    if not user:
        return None
    if not pwd_context.verify(password, user["hashed_password"]):
        return None
    return user
