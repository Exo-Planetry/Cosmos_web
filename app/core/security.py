import base64, hashlib, hmac, json, secrets, time
from typing import Optional
from fastapi import HTTPException, Request
from app.core.config import SECRET


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()


def verify_password(password: str, encoded: str) -> bool:
    try:
        _, salt_b64, digest_b64 = encoded.split("$", 2)
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def _b64(obj: bytes) -> str:
    return base64.urlsafe_b64encode(obj).rstrip(b"=").decode()


def create_token(subject: str, role: str = "researcher", minutes: int = 720) -> str:
    header = _b64(json.dumps({"alg":"HS256","typ":"JWT"}, separators=(",", ":")).encode())
    payload = _b64(json.dumps({"sub":subject,"role":role,"exp":int(time.time()) + minutes*60}, separators=(",", ":")).encode())
    sig = _b64(hmac.new(SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


def decode_token(token: str) -> Optional[dict]:
    try:
        header, payload, signature = token.split(".")
        expected = _b64(hmac.new(SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected): return None
        data = json.loads(base64.urlsafe_b64decode(payload + "=="))
        if int(data.get("exp", 0)) < int(time.time()): return None
        return data
    except Exception:
        return None


def current_user(request: Request) -> Optional[dict]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return None
    return decode_token(auth[7:])


def require_user(request: Request) -> dict:
    user = current_user(request)
    if not user: raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_role(request: Request, *roles: str) -> dict:
    user = require_user(request)
    if user.get("role") not in roles: raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user
