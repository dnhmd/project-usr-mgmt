# app/api/v1/endpoints/users.py

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.users import (
    UserListResponse, 
    UserPasswordUpdate, 
    UserResponse, 
    UserRoleChange, 
    UserUpdate
)
from app.core.exceptions import AuthorizationError
from app.db.session import get_db_session
from app.dependencies import get_current_user, require_admin
from app.models.domain import User
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
async def get_users(
        page: int = Query(default=1, ge=1), 
        limit: int = Query(default=20, ge=1, le=100), 
        name: Optional[str] = Query(default=None), 
        is_active: Optional[bool] = Query(default=None), 
        db: AsyncSession = Depends(get_db_session),
        _: User = Depends(require_admin),
) -> UserListResponse:
    user_service = UserService(db)
    total, users = await user_service.get_users(page, limit, name, is_active)
    
    return UserListResponse(users=users, total=total, page=page, limit=limit)

@router.get("/{user_id}")
async def get_user(
        user_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_user)
) -> UserResponse:
    if current_user.id != user_id and current_user.role_id != 2:
        raise AuthorizationError()
    
    user_service = UserService(db)
    user = await user_service.get_user(user_id)

    return UserResponse.model_validate(user)

@router.patch("/{user_id}")
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_user)
) -> UserResponse:
    if current_user.id != user_id and current_user.role_id != 2:
        raise AuthorizationError()
    
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_update.name, user_update.email)

    return UserResponse.model_validate(user)

@router.patch("/{user_id}/password")
async def change_password(
        user_id: int,
        user_password_update: UserPasswordUpdate,
        db: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_user)
) -> UserResponse:
    if current_user.id != user_id:
        raise AuthorizationError()

    user_service = UserService(db)
    user = await user_service.change_password(user_id, user_password_update.old_password, user_password_update.new_password)

    return UserResponse.model_validate(user)

@router.patch("/{user_id}/role")
async def change_role(
        user_id: int,
        user_role_change: UserRoleChange,
        db: AsyncSession = Depends(get_db_session),
        _: User = Depends(require_admin)
) -> UserResponse:
    user_service = UserService(db)
    user = await user_service.change_role(user_id, user_role_change.role_id)

    return UserResponse.model_validate(user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db_session),
        _: User = Depends(require_admin)
) -> None:
    user_service = UserService(db)
    await user_service.delete_user(user_id)