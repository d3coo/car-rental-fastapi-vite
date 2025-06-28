"""
FastAPI main application with DDD architecture
"""

from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.interfaces.api.v1.bookings import router as bookings_router
from app.interfaces.api.v1.cars import router as cars_router
from app.interfaces.api.v1.contracts import router as contracts_router
from app.interfaces.api.v1.users import router as users_router
from app.interfaces.middleware.error_handler import add_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    print("🚀 Starting Car Rental System API v3.0 (FastAPI + DDD)")
    yield
    print("🛑 Shutting down Car Rental System API")


def create_app() -> FastAPI:
    """Application factory"""
    settings = get_settings()

    app = FastAPI(
        title="Car Rental System API",
        description="Modern car rental management system with FastAPI and DDD architecture",
        version="3.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add exception handlers
    add_exception_handlers(app)

    # Register API routers
    app.include_router(contracts_router, prefix="/api/v1")
    app.include_router(bookings_router, prefix="/api/v1")
    app.include_router(cars_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")

    # Root endpoint
    @app.get("/")
    async def root():
        return JSONResponse(
            {
                "message": "Car Rental System API v3.0",
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "architecture": "FastAPI + Domain-Driven Design",
                "docs": "/docs",
                "redoc": "/redoc",
            }
        )

    # Health check
    @app.get("/health")
    async def health_check():
        return JSONResponse(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "3.0.0",
                "architecture": "FastAPI + DDD",
            }
        )

    return app


# Create the app instance for uvicorn
app = create_app()


def main():
    """Main entry point for development"""
    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
    )


if __name__ == "__main__":
    main()
