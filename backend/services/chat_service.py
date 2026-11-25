import os

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.database.models import ConversationEntry, UserSetting
from backend.intelligence.router import ModelRouter
from backend.config.settings import settings
from backend.schemas.chat_schema import ChatRequestSchema


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def resolve_provider(self, user_id: int, requested_provider: str | None = None) -> str:
        if requested_provider:
            return requested_provider
        preference = self.db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
        return preference.preferred_provider if preference else settings.default_provider

    def send_message(
        self,
        user_id: int,
        request: ChatRequestSchema,
        provider_name: str | None = None,
    ) -> str:
        provider_name = provider_name or self.resolve_provider(user_id, request.provider)
        try:
            router = ModelRouter({
                "OPENAI_API_KEY": settings.openai_api_key or os.getenv("OPENAI_API_KEY") or "",
                "DEFAULT_PROVIDER": provider_name,
                "LOCAL_AI_URL": settings.local_ai_url,
                "LOCAL_AI_MODEL": settings.local_ai_model,
            })
            response = router.chat(
                request.prompt,
                provider_name=provider_name,
                model=request.model,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

        self.db.add(ConversationEntry(user_id=user_id, role="user", content=request.prompt))
        self.db.add(ConversationEntry(user_id=user_id, role="assistant", content=response))
        self.db.commit()
        return response
