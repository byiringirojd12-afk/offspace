from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List

router = APIRouter()

class MemoryItem(BaseModel):
    key: str
    value: str
    category: str | None = None

class MemorySearchResponse(BaseModel):
    results: List[MemoryItem]

@router.post("/save", response_model=MemoryItem)
def save_memory(item: MemoryItem) -> MemoryItem:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Memory persistence is not implemented yet")

@router.get("/search", response_model=MemorySearchResponse)
def search_memory(query: str) -> MemorySearchResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Memory search is not implemented yet")

@router.delete("/delete/{key}")
def delete_memory(key: str) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Memory deletion is not implemented yet")
