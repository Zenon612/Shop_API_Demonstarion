from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.db import get_db
from app.database.models.models import User, Role, Session
from app.schemas.schemas import UserCreate, UserResponse
from app.core.security import hash_password, verify_password
from app.core.config import settings

auth_router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@auth_router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/minute")  # 5 попыток регистрации в минуту
async def register(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    exists = await db.execute(select(User).where(User.email == user_in.email))
    if exists.scalar_one_or_none():
        raise HTTPException(409, "Email already registered")

    new_user = User(
        name=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        is_active=True,
    )
    db.add(new_user)
    await db.flush()

    if user_in.role_ids:
        roles = await db.execute(select(Role).where(Role.id.in_(user_in.role_ids)))
        new_user.roles.extend(roles.scalars().all())

    await db.commit()
    await db.refresh(new_user)
    return new_user


@auth_router.post("/login")
@limiter.limit("5/minute")  # 5 попыток логина в минуту (защита от brute force)
async def login(
    request: Request,
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db),
    response: Response = None,
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    session = Session(
        user_id=user.id,
        expires_at=datetime.now() + timedelta(hours=24),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:512],
    )
    db.add(session)
    await db.commit()

    response.set_cookie(
        key="session_id",
        value=session.id,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=86400,
    )
    return {"msg": "Authenticated", "user_id": user.id}
