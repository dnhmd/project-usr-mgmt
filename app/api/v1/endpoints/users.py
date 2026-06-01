# app/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.users import UserListResponse
from app.db.session import get_db_session
from app.dependencies import require_admin
from app.models.domain import User
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/users")
async def get_users(page: int, 
                    limit: int, 
                    db: AsyncSession = Depends(get_db_session),
                    _: User = Depends(require_admin)
) -> UserListResponse:
    user_service = UserService(db)
    total, users = await user_service.get_users(page, limit)
    
    return UserListResponse(users=users, total=total, page=page, limit=limit)

