"""Alert management endpoints."""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, require_permission
from app.models import User, Alert
from app.core import Permission, NotFoundException
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


class AlertCreate(BaseModel):
    """Create alert request."""
    dataset_id: str
    name: str
    description: str = ""
    condition: dict
    enabled: bool = True


class AlertUpdate(BaseModel):
    """Update alert request."""
    name: str = None
    description: str = None
    condition: dict = None
    enabled: bool = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(require_permission(Permission.MANAGE_ALERTS)),
    db: AsyncSession = Depends(get_db),
):
    """Create new alert."""
    alert = Alert(
        organization_id=current_user.organization_id,
        dataset_id=alert_data.dataset_id,
        name=alert_data.name,
        description=alert_data.description,
        condition=alert_data.condition,
        enabled=alert_data.enabled,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return {
        "success": True,
        "data": {
            "id": alert.id,
            "name": alert.name,
            "enabled": alert.enabled,
            "created_at": alert.created_at.isoformat(),
        },
    }


@router.get("")
async def list_alerts(
    dataset_id: str = Query(None),
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """List alerts for organization."""
    query = select(Alert).where(Alert.organization_id == current_user.organization_id)

    if dataset_id:
        query = query.where(Alert.dataset_id == dataset_id)

    result = await db.execute(query.order_by(Alert.created_at.desc()))
    alerts = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": a.id,
                "name": a.name,
                "dataset_id": a.dataset_id,
                "enabled": a.enabled,
                "condition": a.condition,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ],
    }


@router.get("/{alert_id}")
async def get_alert(
    alert_id: UUID,
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Get specific alert."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == str(alert_id),
            Alert.organization_id == current_user.organization_id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise NotFoundException("Alert not found")

    return {
        "success": True,
        "data": {
            "id": alert.id,
            "name": alert.name,
            "condition": alert.condition,
            "enabled": alert.enabled,
            "created_at": alert.created_at.isoformat(),
        },
    }


@router.put("/{alert_id}")
async def update_alert(
    alert_id: UUID,
    alert_data: AlertUpdate,
    current_user: User = Depends(require_permission(Permission.MANAGE_ALERTS)),
    db: AsyncSession = Depends(get_db),
):
    """Update alert."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == str(alert_id),
            Alert.organization_id == current_user.organization_id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise NotFoundException("Alert not found")

    if alert_data.name:
        alert.name = alert_data.name
    if alert_data.description is not None:
        alert.description = alert_data.description
    if alert_data.condition:
        alert.condition = alert_data.condition
    if alert_data.enabled is not None:
        alert.enabled = alert_data.enabled

    await db.commit()
    await db.refresh(alert)

    return {"success": True, "data": {"id": alert.id, "name": alert.name}}


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    current_user: User = Depends(require_permission(Permission.MANAGE_ALERTS)),
    db: AsyncSession = Depends(get_db),
):
    """Delete alert."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == str(alert_id),
            Alert.organization_id == current_user.organization_id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise NotFoundException("Alert not found")

    await db.delete(alert)
    await db.commit()


@router.get("/{alert_id}/evaluate")
async def evaluate_alert(
    alert_id: UUID,
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Evaluate if alert should trigger."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == str(alert_id),
            Alert.organization_id == current_user.organization_id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise NotFoundException("Alert not found")

    eval_result = await AlertService.evaluate_alert(db, alert, alert.dataset_id)

    return {"success": True, "data": eval_result}


@router.get("/{alert_id}/anomalies")
async def get_anomalies(
    alert_id: UUID,
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Detect anomalies for alert dataset."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == str(alert_id),
            Alert.organization_id == current_user.organization_id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise NotFoundException("Alert not found")

    anomalies = await AlertService.detect_anomalies(db, alert.dataset_id)

    return {"success": True, "data": {"anomalies": anomalies, "count": len(anomalies)}}
