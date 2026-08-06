from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.schemas.settings_schema import SettingsUpdateSchema, SettingsResponseSchema
from backend.services.settings_service import SettingsService
from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user

router = APIRouter()

@router.put("/", response_model=SettingsResponseSchema)
def update_settings(settings_update: SettingsUpdateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> SettingsResponseSchema:
    return SettingsService(db).update_settings(current_user.id, settings_update)

@router.get("/", response_model=SettingsResponseSchema)
def get_settings(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> SettingsResponseSchema:
    return SettingsService(db).get_settings(current_user.id)
