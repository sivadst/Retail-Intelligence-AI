"""Security utilities for authentication and authorization."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


class TokenData(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    exp: datetime
    iat: datetime
    type: str  # 'access' or 'refresh'


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None:
            return None

        return TokenData(
            sub=user_id,
            exp=datetime.fromtimestamp(payload.get("exp"), timezone.utc),
            iat=datetime.fromtimestamp(payload.get("iat"), timezone.utc),
            type=token_type,
        )
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None
