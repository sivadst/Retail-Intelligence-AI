"""Analytics endpoints."""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user, require_permission
from app.models import User, Dataset
from app.core import Permission, NotFoundException
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


async def verify_dataset_access(dataset_id: UUID, current_user: User, db: AsyncSession):
    """Verify dataset belongs to user's organization."""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == str(dataset_id),
            Dataset.organization_id == current_user.organization_id,
        )
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise NotFoundException(f"Dataset {dataset_id} not found or access denied")
    return dataset


@router.get("/kpis")
async def get_kpis(
    dataset_id: UUID = Query(...),
    date_range: str = Query("last_30d"),
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Get KPIs for a dataset."""
    await verify_dataset_access(dataset_id, current_user, db)
    
    kpis = await AnalyticsService.calculate_kpis(db, dataset_id, date_range)
    return {"success": True, "data": kpis}


@router.get("/sales-trend")
async def get_sales_trend(
    dataset_id: UUID = Query(...),
    granularity: str = Query("daily"),
    date_range: str = Query("last_30d"),
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Get sales trend over time."""
    await verify_dataset_access(dataset_id, current_user, db)
    
    trend = await AnalyticsService.get_sales_trend(db, dataset_id, granularity, date_range)
    return {"success": True, "data": trend}


@router.get("/category-breakdown")
async def get_category_breakdown(
    dataset_id: UUID = Query(...),
    metric: str = Query("sales"),
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Get breakdown by category."""
    await verify_dataset_access(dataset_id, current_user, db)
    
    breakdown = await AnalyticsService.get_category_breakdown(db, dataset_id, metric)
    return {"success": True, "data": breakdown}


@router.get("/regional-performance")
async def get_regional_performance(
    dataset_id: UUID = Query(...),
    metric: str = Query("sales"),
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Get performance by region."""
    await verify_dataset_access(dataset_id, current_user, db)
    
    performance = await AnalyticsService.get_regional_performance(db, dataset_id, metric)
    return {"success": True, "data": performance}


@router.get("/top-products")
async def get_top_products(
    dataset_id: UUID = Query(...),
    limit: int = Query(10),
    sort_by: str = Query("sales"),
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Get top products."""
    await verify_dataset_access(dataset_id, current_user, db)
    
    products = await AnalyticsService.get_top_products(db, dataset_id, limit, sort_by)
    return {"success": True, "data": products}


@router.get("/discount-analysis")
async def get_discount_analysis(
    dataset_id: UUID = Query(...),
    current_user: User = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    """Analyze discount impact."""
    await verify_dataset_access(dataset_id, current_user, db)
    
    analysis = await AnalyticsService.get_discount_analysis(db, dataset_id)
    return {"success": True, "data": analysis}
