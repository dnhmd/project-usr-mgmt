# app/services/user_services.py

from typing import Optional

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, NotFoundError
from app.models.domain import Role, User

class UserService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self, page: int, limit: int):
        count = await self.db.execute(select(func.count()).select_from(User))

        result = await self.db.execute(
            select(User)
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return count.scalar_one(), result.scalars().all()

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
        await self.db.delete(user)

        return user

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def is_password_verified(self, password: str, hashed_password: str):
        if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            return True
        return False