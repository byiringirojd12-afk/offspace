from fastapi import APIRouter
from sqlalchemy import text
from backend.database import engine

router = APIRouter()

@router.get("", summary="Health check")
def health_check() -> dict:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "online", "database": "connected", "version": "1.0.0"}
