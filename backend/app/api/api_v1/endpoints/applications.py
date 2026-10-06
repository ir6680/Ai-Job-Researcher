"""
Phase 5: Job Applications & Human Approval API Endpoints.
Provides endpoints for:
- Listing applications
- Fetching full application package by ID
- Updating user edits (cover letter, question answers, notes)
- Recording human review
- Approving application (READY_FOR_SUBMISSION)
- Fetching cover letter with evidence traceability
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.schemas import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse,
    ApplicationUpdatePayload, ApplicationApprovalRequest, CoverLetterResponse
)
from backend.app.models import Application, Job, MasterCV, TailoredCV, ApplicationReview
from backend.app.services.job_service import ApplicationService
from backend.app.services.application_service.application_engine import ApplicationEngine
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=List[ApplicationResponse])
def get_applications(
    status: Optional[str] = Query(None, description="Filter by status (e.g. DRAFT, REVIEW_REQUIRED, READY_FOR_SUBMISSION)"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    db: Session = Depends(get_db)
):
    """List all job applications and their lifecycle status."""
    query = db.query(Application)
    if status:
        query = query.filter(Application.status.ilike(status))
    if job_id:
        query = query.filter(Application.job_id == job_id)
    return query.order_by(desc(Application.updated_at)).all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application_by_id(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve full application details, candidate profile, answers, and readiness report."""
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return app


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    """Record a new application against a saved job (Phase 1 legacy compatibility)."""
    return ApplicationService.create_application(db, payload)


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: str,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update application status, interview schedules, or notes (legacy compatibility)."""
    updated = ApplicationService.update_application(db, application_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return updated


@router.patch("/{application_id}", response_model=ApplicationResponse)
def patch_application_user_edits(
    application_id: str,
    payload: ApplicationUpdatePayload,
    db: Session = Depends(get_db)
):
    """
    Phase 5: Update manual user edits (cover letter, answers, notes) without modifying Master CV.
    Re-evaluates application readiness upon saving changes.
    """
    try:
        updated = ApplicationEngine.update_user_edits(
            db=db,
            application_id=application_id,
            cover_letter=payload.cover_letter,
            custom_answers=payload.custom_answers,
            notes=payload.notes
        )
        if payload.status:
            # Enforce valid status transition
            valid_statuses = [
                "DRAFT", "REVIEW_REQUIRED", "READY_FOR_SUBMISSION",
                "SUBMITTED", "REJECTED", "WITHDRAWN", "INTERVIEW", "OFFER"
            ]
            if payload.status.upper() == "SUBMITTED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot transition to SUBMITTED in Phase 5. External submission is reserved for Phase 6."
                )
            if payload.status.upper() in valid_statuses:
                updated.status = payload.status.upper()
                db.commit()
                db.refresh(updated)

        if payload.interview_date:
            updated.interview_date = payload.interview_date
            db.commit()
            db.refresh(updated)

        return updated
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to update application edits: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{application_id}/review", response_model=ApplicationResponse)
def review_application(
    application_id: str,
    payload: Optional[ApplicationApprovalRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Record human review check for an application.
    """
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    reviewer = payload.reviewer_name if payload else "Candidate"
    notes = payload.notes if payload else "Reviewed by user"

    app.review_timestamp = datetime.utcnow()
    rev = ApplicationReview(
        application_id=app.id,
        reviewer_name=reviewer,
        decision="REVIEWED",
        notes=notes,
        reviewed_at=datetime.utcnow()
    )
    db.add(rev)
    db.commit()
    db.refresh(app)
    return app


@router.post("/{application_id}/approve", response_model=ApplicationResponse)
def approve_application(
    application_id: str,
    payload: Optional[ApplicationApprovalRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Phase 5: Explicit Human Approval.
    Transitions application from DRAFT/REVIEW_REQUIRED to READY_FOR_SUBMISSION.
    IMPORTANT: Does NOT submit to external websites (Phase 6 boundary).
    """
    reviewer = payload.reviewer_name if payload else "Candidate"
    notes = payload.notes if payload else "Approved by candidate for future submission."

    try:
        approved = ApplicationEngine.approve_application(
            db=db,
            application_id=application_id,
            reviewer_name=reviewer,
            notes=notes
        )
        return approved
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to approve application {application_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{application_id}/cover-letter", response_model=CoverLetterResponse)
def get_application_cover_letter(
    application_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve generated/edited cover letter text and evidence traceability.
    """
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    job = db.query(Job).filter(Job.id == app.job_id).first()
    cover_letter_text = app.cover_letter or ""

    return CoverLetterResponse(
        application_id=app.id,
        job_id=app.job_id,
        company=job.company if job else "Target Company",
        job_title=job.job_title if job else "Target Role",
        cover_letter=cover_letter_text,
        integrity_status="PASS" if "unsupported" not in cover_letter_text.lower() else "REVIEW_REQUIRED",
        evidence_map=app.evidence_map or [],
        created_at=app.created_at
    )
