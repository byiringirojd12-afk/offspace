from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="AI provider integration is not implemented yet")
