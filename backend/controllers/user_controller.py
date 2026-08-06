from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.schemas.user_schema import UserCreateSchema, UserLoginSchema, AuthTokenSchema, UserProfileSchema
from backend.services.user_service import UserService
from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=AuthTokenSchema)
def register_user(request: UserCreateSchema, db: Session = Depends(get_db)) -> AuthTokenSchema:
    return UserService(db).register_user(request)

@router.post("/login", response_model=AuthTokenSchema)
def login_user(request: UserLoginSchema, db: Session = Depends(get_db)) -> AuthTokenSchema:
    return UserService(db).login_user(request)

@router.get("/profile", response_model=UserProfileSchema)
def get_profile(current_user=Depends(get_current_user)) -> UserProfileSchema:
    return UserProfileSchema.from_orm(current_user)
