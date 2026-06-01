# app/model/domain.py

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    # Columns defined using Mapped types
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    hashed_password: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    role: Mapped["Role"] = relationship("Role", back_populates="users")

    def __repr__(self) -> str:
        return f"<User name={self.name!r}, email={self.email!r}>"

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), unique=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")

    def __repr__(self) -> str:
        return f"<Role name={self.name!r}>"