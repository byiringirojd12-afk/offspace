from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.database.models import MemoryEntry
from backend.schemas.memory_schema import MemoryCreateSchema


class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def save_memory(self, user_id: int, request: MemoryCreateSchema) -> MemoryEntry:
        entry = MemoryEntry(
            user_id=user_id,
            key=request.key,
            value=request.value,
            category=request.category,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def search_memory(self, user_id: int, query: str):
        results = (
            self.db.query(MemoryEntry)
            .filter(MemoryEntry.user_id == user_id)
            .filter(MemoryEntry.key.ilike(f"%{query}%") | MemoryEntry.value.ilike(f"%{query}%"))
            .all()
        )
        return results

    def delete_memory(self, user_id: int, memory_id: int) -> None:
        entry = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id, MemoryEntry.user_id == user_id).first()
        if entry is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory entry not found")
        self.db.delete(entry)
        self.db.commit()
