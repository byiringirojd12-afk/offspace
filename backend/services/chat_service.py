from sqlalchemy.orm import Session

from backend.schemas.chat_schema import ChatRequestSchema


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def send_message(self, user_id: int, request: ChatRequestSchema) -> str:
        # This service is a production-ready integration point for the AI engine.
        # It currently returns a placeholder response until the AI service is integrated.
        return f"Received message for user {user_id}. AI response generation is available in the integrated AI service." 
