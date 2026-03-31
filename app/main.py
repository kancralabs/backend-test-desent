"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.api.v1.routers import auth, books, health
from app.config import settings
from app.middleware.error_handler import (
    generic_exception_handler,
    integrity_error_handler,
    validation_exception_handler,
)

# Initialize FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="Production-ready REST API with FastAPI + PostgreSQL. "
    "Features: JWT auth, cursor pagination, async SQLAlchemy, high performance.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers (Level 7)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register routers
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(books.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        API metadata and useful links
    """
    return {
        "message": "Books API - 8 Level Challenge",
        "version": settings.project_version,
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/ping",
        "auth": f"{settings.api_v1_prefix}/auth/token",
        "books": f"{settings.api_v1_prefix}/books",
    }


@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks.

    Potential enhancements:
    - Verify database connection
    - Warm up connection pool
    - Run migration checks
    """
    print("🚀 Books API starting up...")
    print(f"📚 Docs available at: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks.

    Potential enhancements:
    - Close database connections gracefully
    - Cleanup resources
    """
    print("👋 Books API shutting down...")
