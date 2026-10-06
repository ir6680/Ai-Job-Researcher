"""
Phase 6: Controlled Browser-Based Application Agent Package.
"""

from backend.app.services.browser_agent.browser_manager import BrowserManager
from backend.app.services.browser_agent.page_navigator import PageNavigator, NavigationResult
from backend.app.services.browser_agent.form_detector import FormDetector, FormDetectionResult, DetectedField
from backend.app.services.browser_agent.field_mapper import FieldMapper, MappedField
from backend.app.services.browser_agent.form_filler import FormFiller, FilledFieldRecord
from backend.app.services.browser_agent.file_uploader import FileUploader, FileUploadResult
from backend.app.services.browser_agent.validation_service import ValidationService, ApplicationEligibilityCheck
from backend.app.services.browser_agent.submission_service import SubmissionService

__all__ = [
    "BrowserManager",
    "PageNavigator",
    "NavigationResult",
    "FormDetector",
    "FormDetectionResult",
    "DetectedField",
    "FieldMapper",
    "MappedField",
    "FormFiller",
    "FilledFieldRecord",
    "FileUploader",
    "FileUploadResult",
    "ValidationService",
    "ApplicationEligibilityCheck",
    "SubmissionService",
]
