from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.auth.password import hash_password, verify_password
from backend.auth.jwt import create_access_token
from backend.database.models import User
from backend.schemas.user_schema import UserCreateSchema, UserLoginSchema, AuthTokenSchema


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, request: UserCreateSchema) -> AuthTokenSchema:
        existing_user = self.db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user = User(
            email=request.email,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        access_token = create_access_token(subject=str(user.id))
        return AuthTokenSchema(access_token=access_token)

    def login_user(self, request: UserLoginSchema) -> AuthTokenSchema:
        user = self.db.query(User).filter(User.email == request.email, User.is_active.is_(True)).first()
        if user is None or not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        access_token = create_access_token(subject=str(user.id))
        return AuthTokenSchema(access_token=access_token)
