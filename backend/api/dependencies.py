from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.database.session import SessionLocal
from backend.auth.dependencies import get_current_user

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_optional_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return get_current_user(credentials)
