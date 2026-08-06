from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from backend.config.settings import settings


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expiration = datetime.now(timezone.utc) + (expires_delta or timedelta(seconds=settings.token_expiration_seconds))
    payload = {"sub": subject, "exp": expiration}
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expiration = datetime.now(timezone.utc) + (expires_delta or timedelta(seconds=settings.refresh_token_expiration_seconds))
    payload = {"sub": subject, "exp": expiration, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    data = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])
    if data.get("type") == "refresh":
        raise InvalidTokenError("Expected access token, received refresh token")
    return data


def decode_refresh_token(token: str) -> dict:
    data = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])
    if data.get("type") != "refresh":
        raise InvalidTokenError("Expected refresh token")
    return data
