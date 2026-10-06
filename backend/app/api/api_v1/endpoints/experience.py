"""
Experience Management Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import ExperienceCreate, ExperienceResponse
from backend.app.services.master_cv_service import MasterCVService
from backend.app.models import MasterCV

router = APIRouter()


@router.get("", response_model=list[ExperienceResponse])
def list_experience(db: Session = Depends(get_db)):
    """List all work and internship experiences."""
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        return []
    return cv.experience


@router.post("", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
def add_experience(payload: ExperienceCreate, db: Session = Depends(get_db)):
    """Add a work/internship experience entry to Master CV."""
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        user = MasterCVService.get_or_create_default_user(db)
        cv = MasterCV(user_id=user.id, full_name=user.full_name, email=user.email)
        db.add(cv)
        db.commit()
        db.refresh(cv)

    new_exp = MasterCVService.add_experience(db, cv.id, payload)
    return new_exp


@router.delete("/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(exp_id: str, db: Session = Depends(get_db)):
    """Delete an experience record."""
    success = MasterCVService.delete_experience(db, exp_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience record not found")
    return None
