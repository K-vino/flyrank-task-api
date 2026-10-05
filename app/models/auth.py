from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any


class SignUpRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[Any] = None


class UserProfileResponse(BaseModel):
    id: str
    email: Optional[str] = None
    created_at: Optional[str] = None
    app_metadata: Optional[dict] = None
    user_metadata: Optional[dict] = None
