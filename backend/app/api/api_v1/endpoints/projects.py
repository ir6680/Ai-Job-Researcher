"""
Projects Management Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import ProjectCreate, ProjectResponse
from backend.app.services.master_cv_service import MasterCVService
from backend.app.models import MasterCV

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all projects in the Master CV."""
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        return []
    return cv.projects


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def add_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """Add a verified project to the Master CV."""
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        user = MasterCVService.get_or_create_default_user(db)
        cv = MasterCV(user_id=user.id, full_name=user.full_name, email=user.email)
        db.add(cv)
        db.commit()
        db.refresh(cv)

    new_project = MasterCVService.add_project(db, cv.id, payload)
    return new_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Remove a project from Master CV."""
    success = MasterCVService.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return None
