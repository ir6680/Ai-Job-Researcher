"""
Jobs Endpoints - Phase 2 Discovery, Filtering, and Collection.
Provides endpoints to trigger discovery runs, inspect audit metrics,
query jobs with faceted filters, view complete job descriptions, and update statuses.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobStatusUpdate,
    JobDiscoveryRunRequest,
    JobDiscoveryRunResponse,
    JobDiscoverySourceInfo,
    JobMatchEvaluationResponse,
    TailoringRequest,
    TailoredCVResponse,
    PrepareApplicationRequest,
    ApplicationResponse
)
from backend.app.models import TailoredCV, Application
from sqlalchemy import desc
from backend.app.services.job_service import JobService
from backend.app.services.job_discovery.discovery_service import JobDiscoveryService
from backend.app.services.job_discovery.sources.registry import list_source_infos
from backend.app.services.master_cv_service import MasterCVService
from backend.app.services.matching_service import JobMatchingService
from backend.app.services.tailoring.tailoring_engine import CVTailoringEngine
from backend.app.services.application_service.application_engine import ApplicationEngine
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/{job_id}/tailor-cv", response_model=TailoredCVResponse, status_code=status.HTTP_201_CREATED)
def generate_tailored_cv_for_job(
    job_id: str,
    payload: Optional[TailoringRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Phase 4: Generate an evidence-grounded, ATS-friendly tailored CV for this job.
    - Requires job match score >= APPLICATION_THRESHOLD (default 70%), unless force=True.
    - Preserves Master CV immutability.
    - Synthesizes professional summary, prioritizes skills & projects, optimizes bullets.
    - Generates and saves ATS-compliant DOCX and PDF documents.
    """
    from backend.app.api.api_v1.endpoints.tailored_cvs import enrich_tailored_cv_response

    force = payload.force if payload else False
    force_regenerate = payload.force_regenerate if payload else False

    try:
        tailored = CVTailoringEngine.tailor_cv_for_job(
            db=db,
            job_id=job_id,
            force=force,
            force_regenerate=force_regenerate
        )
        return enrich_tailored_cv_response(tailored)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to tailor CV for job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV Tailoring engine encountered an error: {str(e)}"
        )


@router.get("/{job_id}/tailored-cvs", response_model=List[TailoredCVResponse])
def get_job_tailored_cvs(
    job_id: str,
    db: Session = Depends(get_db)
):
    """List all tailored CV versions generated for a specific job."""
    from backend.app.api.api_v1.endpoints.tailored_cvs import enrich_tailored_cv_response
    cvs = db.query(TailoredCV).filter(
        TailoredCV.job_id == job_id
    ).order_by(desc(TailoredCV.version)).all()
    return [enrich_tailored_cv_response(c) for c in cvs]


@router.post("/{job_id}/prepare-application", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def prepare_job_application(
    job_id: str,
    payload: Optional[PrepareApplicationRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Phase 5: Prepare complete evidence-grounded application package for a job.
    - Requires match score >= APPLICATION_THRESHOLD (default 70%), unless force=True.
    - Generates or links Phase 4 Tailored CV.
    - Generates job-specific cover letter with Hallucination Guard.
    - Extracts structured candidate profile and answerable application questions.
    - Runs readiness verification and returns draft application record.
    - Does NOT submit application to external websites.
    """
    force = payload.force if payload else False
    try:
        app_record = ApplicationEngine.prepare_application_package(db=db, job_id=job_id, force=force)
        return app_record
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to prepare application package for job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Application preparation engine encountered an error: {str(e)}"
        )


@router.get("/{job_id}/application", response_model=ApplicationResponse)
def get_job_application(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve prepared application package for a specific job opening.
    """
    app_record = db.query(Application).filter(Application.job_id == job_id).first()
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No application prepared for job '{job_id}'. Use POST /jobs/{job_id}/prepare-application first."
        )
    return app_record


@router.get("/{job_id}/match", response_model=JobMatchEvaluationResponse)
def evaluate_job_match(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Phase 3: Evaluate candidate fit and match score for a specific job against Master CV.
    Returns:
    - Match Score (%)
    - Required Skills (✓)
    - Relevant Experience (✓)
    - Partial Matches (△)
    - Missing Requirements (✗)
    - Recommendation (STRONG MATCH, GOOD MATCH, MODERATE MATCH, WEAK MATCH)
    - Formatted representation report
    """
    job = JobService.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    cv = MasterCVService.get_master_cv(db)
    if not cv:
        # Auto-seed profile if empty
        cv = MasterCVService.seed_candidate_profile_if_empty(db)

    evaluation = JobMatchingService.evaluate_match(job=job, cv=cv, db=db)
    return evaluation


@router.get("/matches/all", response_model=List[JobMatchEvaluationResponse])
def evaluate_all_job_matches(
    db: Session = Depends(get_db)
):
    """
    Phase 3: Evaluate candidate fit across all discovered jobs in the database,
    ranked from highest match score to lowest.
    """
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        cv = MasterCVService.seed_candidate_profile_if_empty(db)

    jobs = JobService.get_jobs(db, limit=100)
    evaluations = [
        JobMatchingService.evaluate_match(job=j, cv=cv, db=db)
        for j in jobs
    ]
    # Rank descending by score
    evaluations.sort(key=lambda x: x.match_score, reverse=True)
    return evaluations


@router.post("/discover", response_model=JobDiscoveryRunResponse, status_code=status.HTTP_200_OK)
async def trigger_job_discovery(
    payload: Optional[JobDiscoveryRunRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Trigger an automated job discovery run.
    Queries official career pages (Systems Ltd, Arbisoft, Devsinc, Tintash, etc.)
    and legitimate job boards for entry-level Lahore software roles.
    Cleans data, validates location and entry-level criteria, and deduplicates against the database.
    """
    try:
        run = await JobDiscoveryService.run_discovery(db=db, request=payload)
        return run
    except Exception as e:
        logger.error(f"Error executing job discovery: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job discovery run encountered an unexpected failure: {str(e)}"
        )


@router.get("/discovery-runs", response_model=List[JobDiscoveryRunResponse])
def get_discovery_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List historical job discovery runs with metrics (added, skipped, filtered)."""
    return JobDiscoveryService.get_discovery_runs(db, skip=skip, limit=limit)


@router.get("/discovery-sources", response_model=List[JobDiscoverySourceInfo])
def get_discovery_sources():
    """List all registered modular job discovery sources."""
    return list_source_infos()


@router.get("", response_model=List[JobResponse])
def get_jobs(
    search: Optional[str] = Query(None, description="Search keyword in title, company, or description"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    source: Optional[str] = Query(None, description="Filter by source (Systems Limited, Arbisoft, Rozee, etc.)"),
    location: Optional[str] = Query(None, description="Filter by location (e.g. Lahore, Remote)"),
    status: Optional[str] = Query(None, description="Filter by status (discovered, saved, ignored, applied, archived)"),
    duplicate_status: Optional[str] = Query("unique", description="Filter by duplicate status (unique, duplicate, or all)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List discovered jobs with faceted filters for company, source, location, keyword, and status.
    """
    dup_filter = None if duplicate_status == "all" else duplicate_status
    return JobDiscoveryService.get_jobs(
        db,
        skip=skip,
        limit=limit,
        search=search,
        company=company,
        source=source,
        location=location,
        status=status,
        duplicate_status=dup_filter
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Retrieve complete collected details for a single job, including raw_description & responsibilities."""
    job = JobService.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.patch("/{job_id}/status", response_model=JobResponse)
def update_job_status(
    job_id: str,
    payload: JobStatusUpdate,
    db: Session = Depends(get_db)
):
    """Mark a job as saved, ignored, applied, or archived."""
    updated = JobDiscoveryService.update_job_status(db, job_id, payload.status)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return updated


@router.post("/{job_id}/refresh", response_model=JobResponse)
def refresh_job(job_id: str, db: Session = Depends(get_db)):
    """Manually re-clean, normalize, and extract responsibilities for a job."""
    refreshed = JobDiscoveryService.refresh_job(db, job_id)
    if not refreshed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return refreshed


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    """Manually add a new job opening to the database."""
    return JobService.create_job(db, payload)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: str, payload: JobUpdate, db: Session = Depends(get_db)):
    """Update job details or requirements."""
    updated = JobService.update_job(db, job_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return updated


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Delete a job record."""
    success = JobService.delete_job(db, job_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return None


@router.post("/seed-lahore-defaults", status_code=status.HTTP_200_OK)
def seed_starter_jobs(db: Session = Depends(get_db)):
    """Seed curated starter jobs from top Lahore software houses if database is empty."""
    count = JobService.seed_starter_jobs_if_empty(db)
    return {"message": f"Seeded {count} Lahore entry-level software house opportunities."}
