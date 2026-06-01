"""Dataset management routes."""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user, require_permission
from app.models import User, Dataset
from app.schemas import DatasetResponse
from app.core import Permission, NotFoundException
import aiofiles
import os
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["datasets"])

UPLOAD_DIR = "storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission(Permission.CREATE_DATASET)),
    db: AsyncSession = Depends(get_db),
) -> DatasetResponse:
    """Upload a dataset file."""
    # Validate file type
    allowed_types = ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
    if file.content_type not in allowed_types:
        raise ValueError(f"File type {file.content_type} not supported")

    try:
        # Save file
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split(".")[-1]
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_extension}")

        file_size = 0
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            file_size = len(content)
            await f.write(content)

        # Create dataset record
        dataset = Dataset(
            name=file.filename,
            organization_id=current_user.organization_id,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension,
            processing_status="pending",
        )

        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)

        logger.info(f"Dataset uploaded: {dataset.id} by {current_user.email}")

        # TODO: Trigger async processing task with Celery
        return DatasetResponse.from_orm(dataset)

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise


@router.get("", response_model=list[DatasetResponse])
async def list_datasets(
    current_user: User = Depends(require_permission(Permission.READ_DATASET)),
    db: AsyncSession = Depends(get_db),
) -> list[DatasetResponse]:
    """List all datasets for organization."""
    result = await db.execute(
        select(Dataset).where(Dataset.organization_id == current_user.organization_id)
    )
    datasets = result.scalars().all()
    return [DatasetResponse.from_orm(d) for d in datasets]


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(require_permission(Permission.READ_DATASET)),
    db: AsyncSession = Depends(get_db),
) -> DatasetResponse:
    """Get dataset by ID."""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.organization_id == current_user.organization_id,
        )
    )
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise NotFoundException(f"Dataset {dataset_id} not found")

    return DatasetResponse.from_orm(dataset)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(require_permission(Permission.DELETE_DATASET)),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete dataset by ID."""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.organization_id == current_user.organization_id,
        )
    )
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise NotFoundException(f"Dataset {dataset_id} not found")

    # Delete file
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)

    await db.delete(dataset)
    await db.commit()

    logger.info(f"Dataset deleted: {dataset_id} by {current_user.email}")
