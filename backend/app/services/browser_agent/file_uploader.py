"""
File Uploader Component for Phase 6 Controlled Browser-Based Application Agent.
Guarantees CV integrity and safety during browser file uploads:
- Verifies that file exists on disk.
- Verifies job_id matches target job.
- Verifies tailored_cv_id matches approved application package.
- Verifies integrity_status == 'PASS'.
- STRICT: NEVER uploads the Master CV when a tailored CV is required.
- Prefers PDF format, falling back to DOCX if requested.
"""

import os
from typing import Optional, Dict, Any, Tuple
from playwright.sync_api import Page
from backend.app.models import TailoredCV, Application
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class FileUploadResult:
    def __init__(
        self,
        success: bool,
        uploaded_path: Optional[str] = None,
        filename: Optional[str] = None,
        file_format: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        self.success = success
        self.uploaded_path = uploaded_path
        self.filename = filename
        self.file_format = file_format
        self.error_code = error_code
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "uploaded_path": self.uploaded_path,
            "filename": self.filename,
            "file_format": self.file_format,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }


class FileUploader:
    """
    Safely verifies and uploads the approved tailored CV document.
    """

    @classmethod
    def verify_and_select_cv_file(
        cls,
        application: Application,
        tailored_cv: Optional[TailoredCV]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates the tailored CV artifact against application requirements.
        Returns (is_valid, file_path, error_message).
        """
        if not tailored_cv:
            return False, None, "No tailored CV record provided for application."

        # 1. Verify job_id match
        if str(tailored_cv.job_id) != str(application.job_id):
            return False, None, (
                f"Security mismatch: Tailored CV job_id '{tailored_cv.job_id}' "
                f"does not match application job_id '{application.job_id}'."
            )

        # 2. Verify tailored_cv_id match
        if application.tailored_cv_id and str(tailored_cv.id) != str(application.tailored_cv_id):
            return False, None, (
                f"Security mismatch: Approved tailored_cv_id '{application.tailored_cv_id}' "
                f"does not match CV id '{tailored_cv.id}'."
            )

        # 3. Verify integrity status
        if tailored_cv.integrity_status != "PASS":
            return False, None, (
                f"Tailored CV integrity status is '{tailored_cv.integrity_status}', "
                "must be 'PASS' before upload."
            )

        # 4. Strictly prevent Master CV upload
        # Tailored CV files reside in exports/tailored_cvs/
        pdf_path = tailored_cv.pdf_path
        docx_path = tailored_cv.docx_path

        selected_path = None
        if pdf_path and os.path.exists(pdf_path):
            selected_path = pdf_path
        elif docx_path and os.path.exists(docx_path):
            selected_path = docx_path

        if not selected_path:
            return False, None, f"Neither PDF ({pdf_path}) nor DOCX ({docx_path}) exists on disk."

        # Safety check: ensure file is not the master CV raw source
        filename = os.path.basename(selected_path).lower()
        if "master_cv" in filename or "master" in filename:
            return False, None, "Security violation: Master CV detected in tailored upload path."

        return True, selected_path, None

    @classmethod
    def upload_cv_to_page(
        cls,
        page: Page,
        application: Application,
        tailored_cv: Optional[TailoredCV],
        file_input_selector: Optional[str] = None
    ) -> FileUploadResult:
        """
        Finds the file input on the page and uploads the validated tailored CV.
        """
        # Validate CV artifact
        is_valid, file_path, err_msg = cls.verify_and_select_cv_file(application, tailored_cv)
        if not is_valid or not file_path:
            logger.error(f"CV verification failed: {err_msg}")
            return FileUploadResult(
                success=False,
                error_code="CV_VERIFICATION_FAILED",
                error_message=err_msg
            )

        filename = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        # Find file input
        selector = file_input_selector or "input[type='file']"
        try:
            file_input = page.locator(selector).first
            count = file_input.count()
            if count == 0:
                logger.warning("No file input element found on the application page.")
                return FileUploadResult(
                    success=False,
                    error_code="NO_FILE_INPUT_FOUND",
                    error_message="Could not locate file upload input on the page."
                )

            # Upload the file
            file_input.set_input_files(file_path)
            logger.info(f"Successfully uploaded approved tailored CV: {filename} ({file_path})")

            return FileUploadResult(
                success=True,
                uploaded_path=file_path,
                filename=filename,
                file_format=ext.replace(".", "").upper()
            )

        except Exception as e:
            err = str(e)
            logger.error(f"Failed to upload CV file: {err}")
            return FileUploadResult(
                success=False,
                error_code="UPLOAD_EXECUTION_ERROR",
                error_message=f"Browser file upload failed: {err}"
            )
