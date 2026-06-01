"""Authentication service."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Organization
from app.schemas import UserCreate, UserLogin
from app.core import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    UnauthorizedException,
    ConflictException,
    NotFoundException,
)
from datetime import datetime

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user registration and login."""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        user_data: UserCreate,
    ) -> tuple[User, str, str]:
        """Register new user and return user + tokens."""
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise ConflictException(f"Email {user_data.email} already registered")

        # Create or get organization
        org_name = user_data.organization_name or f"{user_data.full_name}'s Organization"
        result = await db.execute(select(Organization).where(Organization.name == org_name))
        org = result.scalar_one_or_none()

        if not org:
            org = Organization(name=org_name)
            db.add(org)
            await db.flush()

        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            organization_id=org.id,
            role="owner" if not org.users else "analyst",  # First user is owner
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        logger.info(f"User registered: {user.email}")
        return user, access_token, refresh_token

    @staticmethod
    async def login_user(
        db: AsyncSession,
        login_data: UserLogin,
    ) -> tuple[User, str, str]:
        """Authenticate user and return tokens."""
        result = await db.execute(select(User).where(User.email == login_data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        logger.info(f"User logged in: {user.email}")
        return user, access_token, refresh_token

    @staticmethod
    async def get_user(db: AsyncSession, user_id: str) -> User:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException(f"User {user_id} not found")

        return user

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: str,
        old_password: str,
        new_password: str,
    ) -> User:
        """Change user password."""
        user = await AuthService.get_user(db, user_id)

        if not verify_password(old_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await db.commit()
        await db.refresh(user)

        logger.info(f"Password changed for user: {user.email}")
        return user
