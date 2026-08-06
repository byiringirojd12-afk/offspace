from sqlalchemy.orm import Session

from backend.schemas.settings_schema import SettingsUpdateSchema


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def update_settings(self, user_id: int, settings_update: SettingsUpdateSchema):
        # Placeholder for settings persistence and retrieval.
        return {
            "preferred_provider": settings_update.preferred_provider or "openai",
            "voice_enabled": settings_update.voice_enabled if settings_update.voice_enabled is not None else True,
            "notifications_enabled": settings_update.notifications_enabled if settings_update.notifications_enabled is not None else False,
        }

    def get_settings(self, user_id: int):
        return {
            "preferred_provider": "openai",
            "voice_enabled": True,
            "notifications_enabled": False,
        }
