# app/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.auth import LoginRequest, TokenResponse
from app.api.v1.schemas.users import UserCreate
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    role_id = 1
    user_service = UserService(db)
    user = await user_service.create_user(user_create.name, user_create.email, user_create.password, role_id)
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "iss": "private server",
        }
    )

    return TokenResponse(access_token=access_token)

@router.post("/login")
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    user_service = UserService(db)
    user = await user_service.get_by_email(login_request.email)
    if user is None:
        raise AuthenticationError("Provided credentials are invalid")
    if not user_service.is_password_verified(login_request.password, user.hashed_password):
        raise AuthenticationError("Provided credentials are invalid")
    access_token = create_access_token(
        {
            "sub": str(user.id), 
            "iss": "private server",
        }
    )
     
    return TokenResponse(access_token=access_token)