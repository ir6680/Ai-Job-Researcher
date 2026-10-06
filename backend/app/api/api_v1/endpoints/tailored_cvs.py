"""
Phase 4: Tailored CVs API Endpoints.
Provides endpoints for:
- Retrieving tailored CV by ID
- Inspecting evidence traceability metadata
- Downloading ATS-friendly DOCX and PDF documents
- Marking human review approval
"""

import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import TailoredCV
from backend.app.schemas import TailoredCVResponse
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


def enrich_tailored_cv_response(t: TailoredCV) -> TailoredCVResponse:
    """Helper to attach download URLs to TailoredCVResponse."""
    return TailoredCVResponse(
        id=t.id,
        master_cv_id=t.master_cv_id,
        job_id=t.job_id,
        version=t.version,
        target_company=t.target_company,
        target_role=t.target_role,
        match_score=t.match_score,
        ats_keyword_coverage=t.ats_keyword_coverage,
        integrity_status=t.integrity_status,
        human_reviewed=t.human_reviewed,
        structured_content=t.structured_content or {},
        tailoring_changes=t.tailoring_changes or {},
        evidence_map=t.evidence_map or [],
        rejected_claims=t.rejected_claims or [],
        matched_keywords=t.matched_keywords or [],
        missing_keywords=t.missing_keywords or [],
        docx_path=t.docx_path,
        pdf_path=t.pdf_path,
        docx_download_url=f"/api/v1/tailored-cvs/{t.id}/download/docx" if t.docx_path else None,
        pdf_download_url=f"/api/v1/tailored-cvs/{t.id}/download/pdf" if t.pdf_path else None,
        tailored_content=t.tailored_content,
        highlighted_skills=t.highlighted_skills,
        generated_at=t.generated_at,
        created_at=t.created_at,
        updated_at=t.updated_at
    )


@router.get("/{cv_id}", response_model=TailoredCVResponse)
def get_tailored_cv_by_id(
    cv_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve complete tailored CV record, including structured sections and tailoring audit."""
    t = db.query(TailoredCV).filter(TailoredCV.id == cv_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tailored CV not found")
    return enrich_tailored_cv_response(t)


@router.get("/{cv_id}/evidence", response_model=List[Dict[str, Any]])
def get_tailored_cv_evidence(
    cv_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve full evidence map traceability for every modified or generated bullet/section."""
    t = db.query(TailoredCV).filter(TailoredCV.id == cv_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tailored CV not found")
    return t.evidence_map or []


@router.get("/{cv_id}/download/docx")
def download_tailored_cv_docx(
    cv_id: str,
    db: Session = Depends(get_db)
):
    """Download ATS-compliant DOCX version of the tailored CV."""
    t = db.query(TailoredCV).filter(TailoredCV.id == cv_id).first()
    if not t or not t.docx_path or not os.path.exists(t.docx_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DOCX file not found on server")

    filename = os.path.basename(t.docx_path)
    return FileResponse(
        path=t.docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )


@router.get("/{cv_id}/download/pdf")
def download_tailored_cv_pdf(
    cv_id: str,
    db: Session = Depends(get_db)
):
    """Download ATS-compliant PDF version of the tailored CV."""
    t = db.query(TailoredCV).filter(TailoredCV.id == cv_id).first()
    if not t or not t.pdf_path or not os.path.exists(t.pdf_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF file not found on server")

    filename = os.path.basename(t.pdf_path)
    return FileResponse(
        path=t.pdf_path,
        media_type="application/pdf",
        filename=filename
    )


@router.post("/{cv_id}/review", response_model=TailoredCVResponse)
def mark_human_reviewed(
    cv_id: str,
    db: Session = Depends(get_db)
):
    """Record mandatory human review approval before application submission."""
    t = db.query(TailoredCV).filter(TailoredCV.id == cv_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tailored CV not found")

    t.human_reviewed = True
    db.commit()
    db.refresh(t)
    return enrich_tailored_cv_response(t)
