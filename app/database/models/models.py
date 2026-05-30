import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Table,
    Column,
    ForeignKey,
)
from typing import Optional


class Base(DeclarativeBase):
    pass


user_roles_table = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="roles", secondary=user_roles_table
    )


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, primary_key=True
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, index=True, default=True
    )
    email: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    roles: Mapped[list["Role"]] = relationship(
        "Role", back_populates="users", secondary=user_roles_table, lazy="selectin"
    )


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: secrets.token_hex(32)
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    user: Mapped["User"] = relationship("User", lazy="joined")


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
