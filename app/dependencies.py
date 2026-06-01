# app/dependencies.py

from typing import Annotated, Optional
from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import verify_token
from app.db.session import get_db_session
from app.models.domain import Role, User
from app.services.user_service import UserService


async def get_current_user(
        authorization: Annotated[Optional[str], Header()] = None,
        db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Dependency that extracts and validates the current user.
    Raises 401 if authentication fails.
    """

    if not authorization:
        raise AuthenticationError("Authorization header missing")
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise AuthenticationError("Invalid authorization header format")
    
    # Verify token and get user ID
    payload = verify_token(token)
    
    # Fetch user from database
    user_service = UserService(db)
    user = await user_service.get_user(int(payload["sub"]))
    
    return user

async def require_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    result = await db.execute(
        select(Role)
        .where(Role.id == current_user.role_id)
    )
    role = result.scalar_one_or_none()
    if not role or role.name != "admin":
        raise AuthorizationError("Admin priviledges required")
    return current_user