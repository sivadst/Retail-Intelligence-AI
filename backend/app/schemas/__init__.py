"""Pydantic schemas for validation and serialization."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.core.permissions import Role


class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class OrganizationCreate(OrganizationBase):
    """Create organization schema."""
    pass


class OrganizationResponse(OrganizationBase):
    """Organization response schema."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """Create user schema."""
    password: str = Field(..., min_length=8, max_length=128)
    organization_name: Optional[str] = None  # For registration


class UserLogin(BaseModel):
    """Login schema."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema."""
    id: str
    role: Role
    organization_id: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class DatasetBase(BaseModel):
    """Base dataset schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class DatasetResponse(DatasetBase):
    """Dataset response schema."""
    id: str
    organization_id: str
    file_size: int
    file_type: str
    row_count: Optional[int]
    column_count: Optional[int]
    processing_status: str
    processing_error: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    """Create chat message schema."""
    conversation_id: str
    content: str = Field(..., min_length=1, max_length=5000)


class ChatMessageResponse(BaseModel):
    """Chat message response schema."""
    id: str
    conversation_id: str
    message_type: str
    content: str
    sql_query: Optional[str]
    chart_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    """Create alert schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    condition: dict  # {metric, operator, threshold}


class AlertResponse(AlertCreate):
    """Alert response schema."""
    id: str
    organization_id: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
