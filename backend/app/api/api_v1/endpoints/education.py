"""
Education and Certifications Management Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import (
    EducationCreate,
    EducationResponse,
    CertificationCreate,
    CertificationResponse
)
from backend.app.services.master_cv_service import MasterCVService
from backend.app.models import Certification

education_router = APIRouter()
cert_router = APIRouter()


@education_router.get("", response_model=list[EducationResponse])
def list_education(db: Session = Depends(get_db)):
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        return []
    return cv.education


@education_router.post("", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
def add_education(payload: EducationCreate, db: Session = Depends(get_db)):
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        user = MasterCVService.get_or_create_default_user(db)
        from backend.app.models import MasterCV
        cv = MasterCV(user_id=user.id, full_name=user.full_name, email=user.email)
        db.add(cv)
        db.commit()
        db.refresh(cv)
    return MasterCVService.add_education(db, cv.id, payload)


@education_router.delete("/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(edu_id: str, db: Session = Depends(get_db)):
    success = MasterCVService.delete_education(db, edu_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found")
    return None


@cert_router.get("", response_model=list[CertificationResponse])
def list_certifications(db: Session = Depends(get_db)):
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        return []
    return cv.certifications


@cert_router.post("", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
def add_certification(payload: CertificationCreate, db: Session = Depends(get_db)):
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        user = MasterCVService.get_or_create_default_user(db)
        from backend.app.models import MasterCV
        cv = MasterCV(user_id=user.id, full_name=user.full_name, email=user.email)
        db.add(cv)
        db.commit()
        db.refresh(cv)
    
    cert = Certification(master_cv_id=cv.id, **payload.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@cert_router.delete("/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(cert_id: str, db: Session = Depends(get_db)):
    c = db.query(Certification).filter(Certification.id == cert_id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found")
    db.delete(c)
    db.commit()
    return None
