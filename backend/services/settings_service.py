from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.database.models import UserSetting
from backend.schemas.settings_schema import SettingsUpdateSchema


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def update_settings(self, user_id: int, settings_update: SettingsUpdateSchema):
        entry = self.db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
        if entry is None:
            entry = UserSetting(user_id=user_id)
            self.db.add(entry)
        if settings_update.preferred_provider is not None:
            if settings_update.preferred_provider not in {"openai", "local"}:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="preferred_provider must be 'openai' or 'local'")
            entry.preferred_provider = settings_update.preferred_provider
        if settings_update.voice_enabled is not None:
            entry.voice_enabled = settings_update.voice_enabled
        if settings_update.notifications_enabled is not None:
            entry.notifications_enabled = settings_update.notifications_enabled
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_settings(self, user_id: int):
        entry = self.db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
        if entry is None:
            entry = UserSetting(user_id=user_id)
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
        return entry
