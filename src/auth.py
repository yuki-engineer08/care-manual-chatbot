import hashlib
import hmac
import os
import secrets
import time

from dotenv import load_dotenv
from fastapi import Cookie, HTTPException, status

from sessions import is_session_revoked, revoke_session

load_dotenv()

SESSION_COOKIE_NAME = "staff_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days


def _get_staff_password() -> str:
    return os.environ.get("STAFF_PASSWORD", "")


def _secret_key() -> bytes:
    # Derived from the staff password so no extra secret needs to be
    # configured separately; changing the password invalidates old tokens.
    return _get_staff_password().encode("utf-8")


def _sign(payload: str) -> str:
    return hmac.new(_secret_key(), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_token() -> str:
    """Create a signed session token valid for SESSION_MAX_AGE_SECONDS.

    Each token carries a random session id so it can be individually
    revoked server-side (e.g. on logout), independent of any other
    session created from the same password.
    """
    issued_at = str(int(time.time()))
    session_id = secrets.token_urlsafe(16)
    payload = f"{issued_at}.{session_id}"
    signature = _sign(payload)
    return f"{payload}.{signature}"


def get_session_id(token: str) -> str | None:
    """Extract the session id from a token without verifying it."""
    if not token:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    _, session_id, _ = parts
    return session_id


def verify_session_token(token: str) -> bool:
    if not token:
        return False
    parts = token.split(".")
    if len(parts) != 3:
        return False
    issued_at_str, session_id, signature = parts
    if not issued_at_str.isdigit():
        return False
    payload = f"{issued_at_str}.{session_id}"
    expected_signature = _sign(payload)
    if not hmac.compare_digest(expected_signature, signature):
        return False
    issued_at = int(issued_at_str)
    if time.time() - issued_at > SESSION_MAX_AGE_SECONDS:
        return False
    if is_session_revoked(session_id):
        return False
    return True


def logout_session(token: str) -> None:
    """Revoke the session associated with this token, if any."""
    session_id = get_session_id(token)
    if session_id:
        revoke_session(session_id)


def verify_password(password: str) -> bool:
    expected = _get_staff_password()
    if not expected:
        return False
    return hmac.compare_digest(password, expected)


def require_auth(staff_session: str | None = Cookie(default=None)) -> None:
    if not verify_session_token(staff_session or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
