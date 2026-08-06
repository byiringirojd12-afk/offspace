from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.schemas.chat_schema import ChatRequestSchema, ChatResponseSchema
from backend.services.chat_service import ChatService
from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/message", response_model=ChatResponseSchema)
def send_message(request: ChatRequestSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ChatResponseSchema:
    response_text = ChatService(db).send_message(current_user.id, request)
    return ChatResponseSchema(response=response_text, provider=request.provider or "default")
