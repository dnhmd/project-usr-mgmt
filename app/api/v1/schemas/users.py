# app/api/v1/schemas/users.py

from typing import List, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    
    name: str
    email: str
    password: str = Field(min_length=8)
    
class UserUpdate(BaseModel):

    name: Optional[str] = None
    email: Optional[str] = None

class UserPasswordUpdate(BaseModel):

    old_password: str
    new_password: str
    
class UserRoleChange(BaseModel):

    role_id: int

class UserResponse(BaseModel):

    id: int
    name: str
    email: str
    is_active: bool
    role_id: int

    model_config = {"from_attributes": True}

class UserListResponse(BaseModel):

    users: List[UserResponse]
    total: int
    page: int
    limit: int