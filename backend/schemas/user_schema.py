from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserProfileSchema(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool

    model_config = {
        "from_attributes": True,
    }


class AuthTokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
