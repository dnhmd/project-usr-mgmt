# app/api/v1/schemas/auth.py

from pydantic import BaseModel

class LoginRequest(BaseModel):

    email: str
    password: str

class TokenResponse(BaseModel):
    
    access_token: str
    token_type: str = "bearer"