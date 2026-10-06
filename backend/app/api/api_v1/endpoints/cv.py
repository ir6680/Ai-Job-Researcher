"""
Master CV API Endpoints.
Covers file upload (PDF/DOCX/TXT), deterministic parsing, viewing, and updating.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas import (
    MasterCVFullResponse,
    MasterCVUpdate,
    ExtractedCVData
)
from backend.app.services.cv_parser_service import CVParserService
from backend.app.services.master_cv_service import MasterCVService
from backend.app.utils.file_extractor import extract_text
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=MasterCVFullResponse)
def get_master_cv(db: Session = Depends(get_db)):
    """Retrieve the primary Master CV with all skills, education, experience, and projects."""
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Master CV found. Please upload a CV or create one manually."
        )
    return cv


@router.put("", response_model=MasterCVFullResponse)
def update_master_cv(payload: MasterCVUpdate, db: Session = Depends(get_db)):
    """Update core personal information and links in the Master CV."""
    cv = MasterCVService.get_master_cv(db)
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Master CV found to update."
        )
    updated = MasterCVService.update_master_cv(db, cv.id, payload)
    return updated


@router.post("/upload", response_model=MasterCVFullResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_import_cv(
    file: UploadFile = File(...),
    auto_save: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Upload CV document (PDF, DOCX, or TXT).
    Extracts text, parses structured data factually without inventing information,
    and saves/updates the Master CV record.
    """
    allowed_extensions = [".pdf", ".docx", ".doc", ".txt"]
    filename = file.filename or "uploaded_cv.pdf"
    lower_name = filename.lower()
    
    if not any(lower_name.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Please upload a PDF, DOCX, or TXT file."
        )

    try:
        content_bytes = await file.read()
        if len(content_bytes) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

        # Extract factual text
        raw_text = extract_text(filename, content_bytes)
        if not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract readable text from the document. The file might be an image scan or password-protected."
            )

        # Parse without fabrication
        parsed = CVParserService.parse(raw_text, filename=filename)

        if auto_save:
            saved_cv = MasterCVService.save_extracted_cv(db, parsed)
            return saved_cv
        else:
            # If not auto-saving, we can return the parsed preview (or save anyway)
            saved_cv = MasterCVService.save_extracted_cv(db, parsed)
            return saved_cv

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error handling CV upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CV: {str(e)}"
        )


@router.post("/parse-preview", response_model=ExtractedCVData)
async def parse_cv_preview(file: UploadFile = File(...)):
    """
    Extract and preview structured information from CV without persisting to database.
    Strictly factual.
    """
    try:
        content_bytes = await file.read()
        raw_text = extract_text(file.filename or "cv.pdf", content_bytes)
        return CVParserService.parse(raw_text, filename=file.filename or "cv.pdf")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
