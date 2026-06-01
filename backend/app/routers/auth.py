"""Authentication routes."""
import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register new user."""
    user, access_token, refresh_token = await AuthService.register_user(db, user_data)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login user."""
    user, access_token, refresh_token = await AuthService.login_user(db, login_data)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user info."""
    return UserResponse.from_orm(current_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
) -> TokenResponse:
    """Refresh access token using refresh token."""
    from app.core import create_access_token, create_refresh_token

    access_token = create_access_token(current_user.id)
    refresh_token = create_refresh_token(current_user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Logout user (revoke tokens)."""
    # In a production system, you would revoke tokens here
    logger.info(f"User logged out: {current_user.email}")
    return None
