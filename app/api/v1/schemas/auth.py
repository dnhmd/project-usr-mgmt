# app/api/v1/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):

    email: EmailStr
    password: str = Field(min_length=8)

class TokenResponse(BaseModel):
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class PasswordResetRequest(BaseModel):

    email: EmailStr

class PasswordResetConfirm(BaseModel):

    new_password: str = Field(min_length=8)
    token: str

class RefreshTokenRequest(BaseModel):

    refresh_token: str