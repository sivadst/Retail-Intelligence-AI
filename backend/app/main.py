"""FastAPI application factory."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth, datasets, ai_assistant
from app.core import UnauthorizedException, ForbiddenException, NotFoundException
from app.database import Base, engine

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    logger.info(f"Starting {settings.app_name} ({settings.environment})")
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="Production-ready Retail Intelligence AI platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.retailintelligence.com"],
    )

    # Exception handlers
    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(request, exc):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc.detail)},
            headers=exc.headers,
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_exception_handler(request, exc):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc.detail)},
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc.detail)},
        )

    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "environment": settings.environment}

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "app": settings.app_name,
            "version": "1.0.0",
            "environment": settings.environment,
        }

    # Include routers
    app.include_router(auth.router)
    app.include_router(datasets.router)
    app.include_router(ai_assistant.router)

    logger.info("FastAPI application created successfully")
    return app


# Create app instance
app = create_app()
