from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.schemas.memory_schema import MemoryCreateSchema, MemoryItemSchema, MemorySearchResponse
from backend.services.memory_service import MemoryService
from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=MemoryItemSchema)
def save_memory(item: MemoryCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> MemoryItemSchema:
    return MemoryService(db).save_memory(current_user.id, item)

@router.get("/search", response_model=MemorySearchResponse)
def search_memory(query: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> MemorySearchResponse:
    return MemorySearchResponse(results=MemoryService(db).search_memory(current_user.id, query))

@router.delete("/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict:
    MemoryService(db).delete_memory(current_user.id, memory_id)
    return {"detail": "Memory deleted"}
