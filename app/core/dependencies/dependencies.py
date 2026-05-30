from fastapi import Depends, HTTPException, Request, Cookie
from app.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database.models.models import User, Session


async def get_current_user(
    session_id: int = Cookie("session_id"),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
) -> User:
    result = await db.execute(
        select(Session).where(
            Session.id == session_id, Session.expires_at > datetime.now()
        )
    )

    session_obj = result.scalar_one_or_none()
    if not session_obj:
        raise HTTPException(status_code=401, detail="Сессия не найдена или истекла")

    if not session_obj.user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")

    return session_obj.user


def require_role(*allowed_roles: str):
    async def role_checker(current_user: User = Depends(get_current_user)):
        user_roles = [role.name for role in current_user.roles]
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=403,
                detail=f"Доступ запрещён. Необходимые права: {allowed_roles}",
            )
        return current_user

    return role_checker
