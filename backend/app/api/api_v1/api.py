"""
API Router aggregator for API v1.
"""

from fastapi import APIRouter
from backend.app.api.api_v1.endpoints.cv import router as cv_router
from backend.app.api.api_v1.endpoints.skills import router as skills_router
from backend.app.api.api_v1.endpoints.projects import router as projects_router
from backend.app.api.api_v1.endpoints.experience import router as exp_router
from backend.app.api.api_v1.endpoints.education import education_router, cert_router
from backend.app.api.api_v1.endpoints.jobs import router as jobs_router
from backend.app.api.api_v1.endpoints.applications import router as apps_router
from backend.app.api.api_v1.endpoints.tailored_cvs import router as tailored_cvs_router
from backend.app.api.api_v1.endpoints.health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(cv_router, prefix="/cv", tags=["Master CV"])
api_router.include_router(skills_router, prefix="/skills", tags=["Skills"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(exp_router, prefix="/experience", tags=["Experience"])
api_router.include_router(education_router, prefix="/education", tags=["Education"])
api_router.include_router(cert_router, prefix="/certifications", tags=["Certifications"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(apps_router, prefix="/applications", tags=["Applications"])
api_router.include_router(tailored_cvs_router, prefix="/tailored-cvs", tags=["Tailored CVs"])
