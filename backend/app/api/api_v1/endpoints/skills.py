"""
Skills Management Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import SkillCreate, SkillResponse
from backend.app.services.master_cv_service import MasterCVService
from backend.app.models import Skill

router = APIRouter()


@router.get("", response_model=list[SkillResponse])
def list_skills(db: Session = Depends(get_db)):
    """List all skills in the Master CV."""
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        return []
    return cv.skills


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def add_skill(payload: SkillCreate, db: Session = Depends(get_db)):
    """Add a new verified skill to the Master CV."""
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        # Create a default Master CV if none exists yet
        user = MasterCVService.get_or_create_default_user(db)
        from backend.app.models import MasterCV
        cv = MasterCV(user_id=user.id, full_name=user.full_name, email=user.email)
        db.add(cv)
        db.commit()
        db.refresh(cv)

    new_skill = MasterCVService.add_skill(db, cv.id, payload)
    return new_skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: str, db: Session = Depends(get_db)):
    """Delete a skill from Master CV."""
    success = MasterCVService.delete_skill(db, skill_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return None
