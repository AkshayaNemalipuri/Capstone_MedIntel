import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from fastapi import Header, HTTPException

SECRET = os.getenv("MEDINTEL_SECRET", "local-demo-secret-change-before-deployment")
TOKEN_SECONDS = 60 * 60 * 8


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return base64.b64encode(salt + digest).decode()


def verify_password(password: str, stored: str) -> bool:
    try:
        raw = base64.b64decode(stored.encode())
        salt, expected = raw[:16], raw[16:]
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": int(time.time()) + TOKEN_SECONDS,
    }
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    signature = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{body}.{signed}"


def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Please log in first.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        body, supplied = token.split(".", 1)
        expected = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).digest()
        supplied_bytes = base64.urlsafe_b64decode(supplied + "=" * (-len(supplied) % 4))
        if not hmac.compare_digest(expected, supplied_bytes):
            raise ValueError()
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if payload["exp"] < int(time.time()):
            raise ValueError()
        if payload["role"] not in ("patient", "doctor"):
            raise ValueError()
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Your session is invalid or expired.")


def require_role(role: str):
    def dependency(user=__import__("fastapi").Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="You do not have permission.")
        return user
    return dependency
