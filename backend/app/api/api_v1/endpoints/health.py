"""
Health & Diagnostic Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models import User, MasterCV, Job, Application

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """System health and database connectivity check."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    counts = {
        "users": db.query(User).count() if db_ok else 0,
        "master_cvs": db.query(MasterCV).count() if db_ok else 0,
        "jobs": db.query(Job).count() if db_ok else 0,
        "applications": db.query(Application).count() if db_ok else 0,
    }

    return {
        "status": "online" if db_ok else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database_connected": db_ok,
        "target_city": settings.TARGET_CITY,
        "counts": counts
    }
