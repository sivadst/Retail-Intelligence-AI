"""Dependency injection and authentication."""
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core import verify_token, UnauthorizedException
from app.models import User
from app.core.permissions import Role, Permission, check_permission

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get authenticated user from JWT token."""
    token = credentials.credentials

    token_data = verify_token(token)
    if not token_data:
        raise UnauthorizedException("Invalid or expired token")

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get authenticated admin user."""
    if current_user.role not in [Role.OWNER, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_permission(permission: Permission):
    """Create dependency that checks permission."""

    async def permission_checker(current_user: User = Depends(get_current_user)):
        try:
            check_permission(current_user.role, permission)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        return current_user

    return permission_checker
