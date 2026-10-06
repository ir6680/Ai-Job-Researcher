"""
Main FastAPI Application Entrypoint.
Phase 1: Foundation for Lahore AI Job Application Agent.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.config import settings
from backend.app.database import init_db, SessionLocal
from backend.app.services.job_service import JobService
from backend.app.services.master_cv_service import MasterCVService
from backend.app.api.api_v1.api import api_router
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context: initialize DB and seed starters."""
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    try:
        init_db()
        db = SessionLocal()
        try:
            # Seed default user
            MasterCVService.get_or_create_default_user(db)
            # Seed starter jobs for Lahore software houses
            JobService.seed_starter_jobs_if_empty(db)
        finally:
            db.close()
        logger.info("Database initialized and starter seed verified.")
    except Exception as e:
        logger.error(f"Failed during lifespan startup: {e}")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
# Lahore AI Job Application Agent - Phase 1 Foundation

Clean REST API for:
* **Master CV Module**: Upload PDF/DOCX/TXT CVs, extract factual data without hallucinations, and manage candidate profiles.
* **Database Models**: PostgreSQL schema with SQLAlchemy for users, master CV, skills, education, experience, projects, certifications, jobs, applications, and tailored CVs.
* **Job Model & Board**: Structured job schema designed for Lahore software houses (Systems Ltd, Arbisoft, Devsinc, Tintash, etc.).
* **Applications Tracker**: Manage job application pipelines from saved to interviews.
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (supports local development and Vite frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "path": str(request.url.path)}
    )

# Include API v1 Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} (Phase 1)",
        "target_city": settings.TARGET_CITY,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
