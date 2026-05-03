import re

from fastapi import HTTPException

USERNAME_RE = re.compile(r"^[a-z][a-z0-9_-]{2,29}$")
RESERVED_USERNAMES = {"me", "admin", "api", "auth", "lists", "users", "u"}


def validate_and_normalize_username(value: str) -> str:
    normalized = value.strip().lower()
    if not USERNAME_RE.match(normalized):
        raise HTTPException(
            status_code=400,
            detail="Username must be 3–30 characters, start with a letter, and use only a–z, 0–9, _ or -.",
        )
    if normalized in RESERVED_USERNAMES:
        raise HTTPException(status_code=400, detail="That username is reserved.")
    return normalized
