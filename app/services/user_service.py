# app/services/user_services.py

from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, NotFoundError, RequestValidationError
from app.models.domain import RefreshToken, Role, User

class UserService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self, page: int, limit: int, name: Optional[str], is_active: Optional[bool]):
        query = select(User)
        count_query = select(func.count()).select_from(User)

        if name is not None:
            query = query.where(User.name == name)
            count_query = count_query.where(User.name == name)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)
        query_result = await self.db.execute(
            query
            .offset((page - 1) * limit)
            .limit(limit)
        )
        count_result = await self.db.execute(count_query)

        return count_result.scalar_one(), query_result.scalars().all()

    async def get_user(self, id: int):
        user = await self.db.get(User, id)
        if user is None:
            raise NotFoundError("User", str(id))
        
        return user

    async def create_user(self, name: str, email: str, password: str, role_id: int):
        salt = bcrypt.gensalt()
        hashed_password = (bcrypt.hashpw(password.encode("utf-8"), salt)).decode("utf-8")

        user = User(name=name, email=email, hashed_password=hashed_password, role_id=role_id)
        self.db.add(user)
        try:
            await self.db.flush()
            await self.db.refresh(user)
        except IntegrityError:
            await self.db.rollback()
            raise RequestValidationError("Email already exists")

        return user

    async def update_user(self, id: int, name: Optional[str] = None, email: Optional[str] = None):
        user = await self.get_user(id)

        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        
        return user
    
    async def change_password(self, id: int, old_password: str, new_password: str):
        user = await self.get_user(id)

        if self.is_password_verified(old_password, user.hashed_password):
            salt = bcrypt.gensalt()
            hashed_new_password = (bcrypt.hashpw(new_password.encode("utf-8"), salt)).decode("utf-8")

            user.hashed_password = hashed_new_password
        else:
            raise AuthenticationError("Entered password is wrong")
        
        return user

    async def change_role(self, id: int, role_id: int):
        role = await self.db.get(Role, role_id)
        if role is None:
            raise NotFoundError("Role", str(role_id))
        
        user = await self.get_user(id)

        user.role_id = role_id

        return user

    async def delete_user(self, id: int):
        user = await self.get_user(id)
        user.is_active = False

        # await self.db.delete(user)

        return user

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def is_password_verified(self, password: str, hashed_password: str):
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    
    async def reset_password(self, id: int, new_password: str):
        user = await self.get_user(id)

        salt = bcrypt.gensalt()
        hashed_new_password = (bcrypt.hashpw(new_password.encode("utf-8"), salt)).decode("utf-8")

        user.hashed_password = hashed_new_password
    
    async def create_refresh_token(self, user_id: int) -> RefreshToken:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7)
        
        refresh_token = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
        self.db.add(refresh_token)
        await self.db.flush()
        await self.db.refresh(refresh_token)

        return refresh_token
    
    async def get_refresh_token(self, token: str) -> RefreshToken:
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.token == token))
        refresh_token = result.scalar_one_or_none()

        if refresh_token is None:
            raise NotFoundError("Refresh Token", str(id))
        
        if refresh_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise AuthenticationError("Refresh token expired. Please login again.")
        
        if refresh_token.is_revoked:
            raise AuthenticationError("Refresh token expired. Please login again.")
        
        return refresh_token
    
    async def revoke_refresh_token(self, token: str) -> None:
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.token == token))
        refresh_token = result.scalar_one_or_none()

        if refresh_token is None:
            raise NotFoundError("Refresh Token", str(id))
        
        if refresh_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise AuthenticationError("Refresh token expired. Please login again.")
        
        refresh_token.is_revoked = True