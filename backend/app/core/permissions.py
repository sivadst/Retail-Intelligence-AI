"""Role-based access control (RBAC) and permissions."""
from enum import Enum
from typing import List
from app.core.exceptions import ForbiddenException


class Role(str, Enum):
    """User roles."""
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(str, Enum):
    """System permissions."""
    # Organization
    MANAGE_ORGANIZATION = "manage_organization"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"

    # Datasets
    CREATE_DATASET = "create_dataset"
    READ_DATASET = "read_dataset"
    DELETE_DATASET = "delete_dataset"

    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_ANALYTICS = "export_analytics"

    # AI
    USE_AI_ASSISTANT = "use_ai_assistant"

    # Alerts
    MANAGE_ALERTS = "manage_alerts"

    # Reports
    CREATE_REPORT = "create_report"
    VIEW_REPORT = "view_report"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.OWNER: [
        Permission.MANAGE_ORGANIZATION,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.CREATE_DATASET,
        Permission.READ_DATASET,
        Permission.DELETE_DATASET,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.USE_AI_ASSISTANT,
        Permission.MANAGE_ALERTS,
        Permission.CREATE_REPORT,
        Permission.VIEW_REPORT,
    ],
    Role.ADMIN: [
        Permission.MANAGE_USERS,
        Permission.CREATE_DATASET,
        Permission.READ_DATASET,
        Permission.DELETE_DATASET,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.USE_AI_ASSISTANT,
        Permission.MANAGE_ALERTS,
        Permission.CREATE_REPORT,
        Permission.VIEW_REPORT,
    ],
    Role.ANALYST: [
        Permission.READ_DATASET,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.USE_AI_ASSISTANT,
        Permission.CREATE_REPORT,
        Permission.VIEW_REPORT,
    ],
    Role.VIEWER: [
        Permission.READ_DATASET,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_REPORT,
    ],
}


def check_permission(user_role: Role, required_permission: Permission) -> None:
    """Check if user has required permission."""
    if required_permission not in ROLE_PERMISSIONS.get(user_role, []):
        raise ForbiddenException(
            detail=f"User role '{user_role}' lacks '{required_permission}' permission"
        )


def has_permission(user_role: Role, required_permission: Permission) -> bool:
    """Check if user has permission (returns boolean)."""
    return required_permission in ROLE_PERMISSIONS.get(user_role, [])
