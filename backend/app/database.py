"""Database connection and session management."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool,
    connect_args={
        "server_settings": {
            "application_name": settings.app_name,
        }
    },
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            await session.close()
