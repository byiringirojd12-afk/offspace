from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/signin", response_model=AuthResponse)
def signin(request: SignInRequest) -> AuthResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is not implemented yet")

@router.post("/signup", response_model=AuthResponse)
def signup(request: SignUpRequest) -> AuthResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication is not implemented yet")
