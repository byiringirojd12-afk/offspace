from pydantic import BaseModel
from typing import Optional


class SettingsUpdateSchema(BaseModel):
    preferred_provider: Optional[str] = None
    voice_enabled: Optional[bool] = None
    notifications_enabled: Optional[bool] = None


class SettingsResponseSchema(BaseModel):
    preferred_provider: str
    voice_enabled: bool
    notifications_enabled: bool
