"""Forecasting endpoints."""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user, require_permission
from app.models import User, Dataset
from app.core import Permission, NotFoundException
from app.services.forecasting_service import ForecastingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/forecasting", tags=["forecasting"])


async def verify_dataset_access(dataset_id: UUID, current_user: User, db: AsyncSession):
    """Verify dataset access."""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == str(dataset_id),
            Dataset.organization_id == current_user.organization_id,
        )
    )
    if not result.scalar_one_or_none():
        raise NotFoundException("Dataset not found or access denied")


@router.post("/forecast")
async def generate_forecast(
    dataset_id: UUID = Query(...),
    metric: str = Query("sales"),
    granularity: str = Query("daily"),
    horizon: int = Query(30),
    current_user: User = Depends(require_permission(Permission.USE_AI_ASSISTANT)),
    db: AsyncSession = Depends(get_db),
):
    """Generate demand forecast."""
    await verify_dataset_access(dataset_id, current_user, db)
    
    forecast = await ForecastingService.generate_forecast(
        db,
        dataset_id,
        metric,
        granularity,
        horizon,
    )
    return {"success": "error" not in forecast, "data": forecast}
