"""
Submission Service Component for Phase 6 Controlled Browser-Based Application Agent.
Orchestrates browser automation steps, enforces submission lock/idempotency,
detects post-submission confirmations, and records immutable audit logs.
"""

import uuid
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from playwright.sync_api import Page

from backend.app.models import Application, Job, TailoredCV, SubmissionAuditLog
from backend.app.services.browser_agent.browser_manager import BrowserManager
from backend.app.services.browser_agent.page_navigator import PageNavigator
from backend.app.services.browser_agent.form_detector import FormDetector, FormDetectionResult
from backend.app.services.browser_agent.field_mapper import FieldMapper, MappedField
from backend.app.services.browser_agent.form_filler import FormFiller
from backend.app.services.browser_agent.file_uploader import FileUploader
from backend.app.services.browser_agent.validation_service import ValidationService
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class SubmissionService:
    """
    Controlled Browser Automation Orchestrator for Phase 6.
    Follows strict state machine transitions and audit logging.
    """

    CONFIRMATION_PATTERNS = [
        re.compile(r"\b(thank\s*you\s*for\s*(applying|your\s*application))\b", re.I),
        re.compile(r"\b(application\s*(has\s*been\s*)?(submitted|received|sent))\b", re.I),
        re.compile(r"\b(we\s*(have\s*)?received\s*your\s*application)\b", re.I),
        re.compile(r"\b(application\s*success(fully)?)\b", re.I),
        re.compile(r"\b(confirmation\s*(number|code|id)\s*[:#]?\s*([a-z0-9\-]+))\b", re.I),
    ]

    @classmethod
    def record_audit_log(
        cls,
        db: Session,
        application_id: str,
        job_id: str,
        url: str,
        browser_action: str,
        fields_populated: Dict[str, Any],
        files_uploaded: List[str],
        human_approval: bool,
        submission_result: str,
        confirmation_result: Optional[str] = None,
        errors: Optional[str] = None
    ) -> SubmissionAuditLog:
        """Creates an immutable audit record for the attempt."""
        audit = SubmissionAuditLog(
            application_id=application_id,
            job_id=job_id,
            url=url,
            browser_action=browser_action,
            fields_populated=fields_populated,
            files_uploaded=files_uploaded,
            human_approval=human_approval,
            submission_result=submission_result,
            confirmation_result=confirmation_result,
            errors=errors,
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        logger.info(f"Audit record logged: {browser_action} -> {submission_result}")
        return audit

    @classmethod
    def prepare_browser_session(
        cls,
        db: Session,
        application_id: str,
        dry_run: bool = True,
        headless: bool = True,
        custom_overrides: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes Steps 1 to 10 of the browser agent:
        1. Eligibility check
        2. Launch browser
        3. Navigate to application URL
        4. Detect form and security barriers (CAPTCHA/OTP/Auth)
        5. Map fields to verified candidate data
        6. Fill verified fields
        7. Upload approved tailored CV (safe dry-run)
        8. Generate pre-submission review snapshot with confirmation token
        """
        app_record = db.query(Application).filter(Application.id == application_id).first()
        if not app_record:
            raise ValueError(f"Application '{application_id}' not found.")

        job = db.query(Job).filter(Job.id == app_record.job_id).first()
        if not job:
            raise ValueError(f"Target job '{app_record.job_id}' not found.")

        tailored_cv = None
        if app_record.tailored_cv_id:
            tailored_cv = db.query(TailoredCV).filter(TailoredCV.id == app_record.tailored_cv_id).first()
        if not tailored_cv:
            tailored_cv = db.query(TailoredCV).filter(TailoredCV.job_id == job.id).first()

        # Step 1: Eligibility check
        eligibility = ValidationService.verify_application_eligibility(app_record, job, tailored_cv)
        if not eligibility.is_eligible:
            err_msg = "; ".join(eligibility.reasons)
            logger.warning(f"Application {application_id} ineligible: {err_msg}")
            app_record.browser_state = {
                "status": "SUBMISSION_BLOCKED",
                "current_step": "ELIGIBILITY_CHECK",
                "last_successful_step": "NONE",
                "error_code": "INELIGIBLE_APPLICATION",
                "error_message": err_msg,
                "timestamp": datetime.utcnow().isoformat()
            }
            db.commit()
            return app_record.browser_state

        target_url = job.source_url or job.application_url or ""
        app_record.submission_url = target_url
        attempt_id = f"attempt_{uuid.uuid4().hex[:12]}"
        app_record.submission_attempt_id = attempt_id

        # Update status to OPENING
        app_record.browser_state = {
            "status": "OPENING",
            "current_step": "NAVIGATING_TO_URL",
            "last_successful_step": "ELIGIBILITY_CHECK",
            "timestamp": datetime.utcnow().isoformat()
        }
        db.commit()

        # Step 2 & 3: Browser Launch and Navigation
        browser_mgr = BrowserManager(headless=headless)
        try:
            context, page = browser_mgr.start_session()

            nav_res = PageNavigator.navigate_to_application_url(
                page=page,
                target_url=target_url,
                expected_company=job.company
            )

            if not nav_res.success:
                status_code = "SUBMISSION_BLOCKED" if nav_res.redirected_unrelated_domain else "FAILED"
                app_record.browser_state = {
                    "status": status_code,
                    "current_step": "NAVIGATION",
                    "last_successful_step": "ELIGIBILITY_CHECK",
                    "error_code": nav_res.error_code,
                    "error_message": nav_res.error_message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                db.commit()
                cls.record_audit_log(
                    db=db,
                    application_id=app_record.id,
                    job_id=job.id,
                    url=target_url,
                    browser_action="NAVIGATION_FAILED",
                    fields_populated={},
                    files_uploaded=[],
                    human_approval=False,
                    submission_result="BLOCKED",
                    errors=nav_res.error_message
                )
                return app_record.browser_state

            # Step 4: Form Detection & Security Barrier Detection
            app_record.browser_state["current_step"] = "DETECTING_FORM"
            app_record.browser_state["last_successful_step"] = "NAVIGATION"
            db.commit()

            detection = FormDetector.detect_form(page)

            # Check security barriers
            if detection.captcha_detected or detection.otp_detected or detection.auth_required:
                barrier_desc = []
                if detection.captcha_detected:
                    barrier_desc.append(f"CAPTCHA ({detection.captcha_type or 'detected'})")
                if detection.otp_detected:
                    barrier_desc.append("OTP Challenge")
                if detection.auth_required:
                    barrier_desc.append("Authentication Gate")

                reason = " | ".join(barrier_desc)
                app_record.browser_state = {
                    "status": "HUMAN_INTERVENTION_REQUIRED",
                    "current_step": "SECURITY_BARRIER_PAUSE",
                    "last_successful_step": "FORM_DETECTION",
                    "captcha_detected": detection.captcha_detected,
                    "otp_detected": detection.otp_detected,
                    "auth_required": detection.auth_required,
                    "error_code": "SECURITY_CHALLENGE_DETECTED",
                    "error_message": f"Paused: {reason}. Agent strictly respects access controls and does not bypass.",
                    "timestamp": datetime.utcnow().isoformat()
                }
                db.commit()
                cls.record_audit_log(
                    db=db,
                    application_id=app_record.id,
                    job_id=job.id,
                    url=page.url,
                    browser_action="SECURITY_BARRIER_PAUSE",
                    fields_populated={},
                    files_uploaded=[],
                    human_approval=False,
                    submission_result="PAUSED",
                    errors=f"Security challenges: {reason}"
                )
                return app_record.browser_state

            # Step 5: Field Mapping
            app_record.browser_state["status"] = "FORM_DETECTED"
            app_record.browser_state["current_step"] = "MAPPING_FIELDS"
            app_record.browser_state["last_successful_step"] = "FORM_DETECTION"
            db.commit()

            mapped_fields = FieldMapper.map_fields(
                detected_fields=detection.fields,
                candidate_profile=app_record.candidate_profile or {},
                application_answers=app_record.application_answers or [],
                cover_letter=app_record.cover_letter,
                custom_overrides=custom_overrides or {}
            )

            # Step 6: Form Filling
            app_record.browser_state["status"] = "FILLING"
            app_record.browser_state["current_step"] = "POPULATING_VERIFIED_FIELDS"
            db.commit()

            filled_records = FormFiller.fill_form(page, mapped_fields)

            # Step 7: File Uploading
            upload_result = FileUploader.upload_cv_to_page(
                page=page,
                application=app_record,
                tailored_cv=tailored_cv
            )

            files_uploaded = [upload_result.filename] if upload_result.success and upload_result.filename else []

            # Step 8: Final Review Snapshot & Confirmation Token Generation
            snapshot = ValidationService.generate_review_snapshot(
                application=app_record,
                job=job,
                tailored_cv=tailored_cv,
                mapped_fields=mapped_fields,
                captcha_detected=detection.captcha_detected,
                otp_detected=detection.otp_detected,
                auth_required=detection.auth_required
            )

            token = snapshot["confirmation_token"]
            app_record.submission_token = token
            app_record.submission_lock = False  # Reset lock for fresh review

            browser_state = {
                "application_id": app_record.id,
                "job_id": job.id,
                "company": job.company,
                "job_title": job.job_title,
                "application_url": target_url,
                "status": "READY_FOR_FINAL_CONFIRMATION",
                "current_step": "WAITING_FOR_EXPLICIT_HUMAN_CONFIRMATION",
                "last_successful_step": "PREPARE_FIELDS_AND_CV",
                "form_detected": detection.form_found,
                "detected_fields": [f.to_dict() for f in detection.fields],
                "mapped_fields": {m.field.name or m.field.field_id: m.to_dict() for m in mapped_fields},
                "fields_requiring_user_input": snapshot["missing_fields"],
                "captcha_detected": False,
                "otp_detected": False,
                "auth_required": False,
                "cv_uploaded": upload_result.success,
                "cv_filename": upload_result.filename,
                "warnings": snapshot["warnings"],
                "confirmation_token": token,
                "can_submit": snapshot["can_submit"],
                "filled_count": len(filled_records),
                "submission_attempt_id": attempt_id,
                "review_snapshot": snapshot,
                "timestamp": datetime.utcnow().isoformat()
            }

            app_record.browser_state = browser_state
            db.commit()

            # Record audit log for the prepare / dry-run action
            cls.record_audit_log(
                db=db,
                application_id=app_record.id,
                job_id=job.id,
                url=page.url,
                browser_action="DRY_RUN_PREPARATION",
                fields_populated={f.name or f.field_id: f.value for f in filled_records},
                files_uploaded=files_uploaded,
                human_approval=False,
                submission_result="DRY_RUN_COMPLETE",
                confirmation_result=None,
                errors="; ".join(snapshot["warnings"]) if snapshot["warnings"] else None
            )

            return browser_state

        finally:
            browser_mgr.close()

    @classmethod
    def confirm_and_submit(
        cls,
        db: Session,
        application_id: str,
        confirmation_token: str,
        reviewer_name: str = "Candidate",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes Step 11 & 12: Controlled Final Submission.
        Requires valid confirmation token, checks submission lock, verifies targets,
        clicks submit, checks confirmation indicators, transitions status, and logs audit record.
        """
        app_record = db.query(Application).filter(Application.id == application_id).first()
        if not app_record:
            raise ValueError(f"Application '{application_id}' not found.")

        job = db.query(Job).filter(Job.id == app_record.job_id).first()
        if not job:
            raise ValueError(f"Job '{app_record.job_id}' not found.")

        # 1. Verify confirmation token
        if not app_record.submission_token or app_record.submission_token != confirmation_token:
            logger.error("Submission rejected: invalid or expired confirmation token.")
            raise ValueError("Invalid or expired confirmation token. Generate a fresh review first.")

        # 2. Check Submission Lock / Idempotency
        if app_record.submission_lock or app_record.status == "SUBMITTED":
            logger.warning("Duplicate submission attempt blocked by submission lock.")
            raise ValueError("Application has already been submitted or submission is in-flight.")

        # 3. Verify application consistency
        if not app_record.submission_url or not job.source_url:
            raise ValueError("Target application URL is missing.")

        target_url = job.source_url or job.application_url or ""
        tailored_cv = None
        if app_record.tailored_cv_id:
            tailored_cv = db.query(TailoredCV).filter(TailoredCV.id == app_record.tailored_cv_id).first()

        # Engage Submission Lock
        app_record.submission_lock = True
        app_record.browser_state["status"] = "SUBMITTING"
        app_record.browser_state["current_step"] = "CLICKING_SUBMIT"
        db.commit()

        browser_mgr = BrowserManager(headless=True)
        try:
            context, page = browser_mgr.start_session()

            # Navigate and fill
            nav = PageNavigator.navigate_to_application_url(page, target_url, expected_company=job.company)
            if not nav.success:
                app_record.submission_lock = False
                app_record.browser_state["status"] = "FAILED"
                app_record.browser_state["error_message"] = nav.error_message
                db.commit()
                raise RuntimeError(f"Navigation failed before submit: {nav.error_message}")

            detection = FormDetector.detect_form(page)
            if detection.captcha_detected or detection.otp_detected or detection.auth_required:
                app_record.submission_lock = False
                app_record.browser_state["status"] = "HUMAN_INTERVENTION_REQUIRED"
                db.commit()
                raise RuntimeError("Security barrier detected during submission execution.")

            mapped = FieldMapper.map_fields(
                detection.fields,
                app_record.candidate_profile or {},
                app_record.application_answers or [],
                app_record.cover_letter
            )
            filled = FormFiller.fill_form(page, mapped)
            FileUploader.upload_cv_to_page(page, app_record, tailored_cv)

            # Click submit button
            submit_selector = detection.submit_button_selector or "button[type='submit'], input[type='submit']"
            try:
                page.locator(submit_selector).first.click()
                page.wait_for_timeout(3000)  # Wait for submission response
            except Exception as e:
                logger.error(f"Failed to click submit button: {e}")

            # Step 12: Post-Submission Verification
            content_after = page.content()
            page_text = page.inner_text("body") if page.locator("body").count() > 0 else ""
            submission_verified = False
            confirmation_message = None
            confirmation_ref = None

            for pattern in cls.CONFIRMATION_PATTERNS:
                match = pattern.search(page_text)
                if match:
                    submission_verified = True
                    confirmation_message = match.group(0)
                    if len(match.groups()) >= 3 and match.group(3):
                        confirmation_ref = match.group(3)
                    break

            # Fallback URL check (e.g. redirected to /thank-you or /success)
            current_path = page.url.lower()
            if any(k in current_path for k in ["thank-you", "thanks", "success", "submitted", "confirmation"]):
                submission_verified = True
                if not confirmation_message:
                    confirmation_message = f"Redirected to confirmation page: {page.url}"

            submitted_at = datetime.utcnow()
            attempt_id = app_record.submission_attempt_id or f"sub_{uuid.uuid4().hex[:12]}"

            if submission_verified:
                app_record.status = "SUBMITTED"
                app_record.applied_at = submitted_at
                app_record.confirmation_message = confirmation_message
                app_record.confirmation_reference = confirmation_ref
                app_record.submission_attempt_id = attempt_id
                # Consume single-use token
                app_record.submission_token = None

                app_record.browser_state = {
                    "status": "SUBMITTED",
                    "current_step": "SUBMISSION_VERIFIED",
                    "last_successful_step": "SUBMISSION_VERIFIED",
                    "confirmation_message": confirmation_message,
                    "confirmation_reference": confirmation_ref,
                    "submitted_at": submitted_at.isoformat(),
                    "submission_attempt_id": attempt_id,
                    "submission_url": page.url,
                    "timestamp": datetime.utcnow().isoformat()
                }
                db.commit()

                cls.record_audit_log(
                    db=db,
                    application_id=app_record.id,
                    job_id=job.id,
                    url=page.url,
                    browser_action="FINAL_SUBMISSION",
                    fields_populated={f.name: f.value for f in filled},
                    files_uploaded=[tailored_cv.pdf_path] if tailored_cv and tailored_cv.pdf_path else [],
                    human_approval=True,
                    submission_result="SUCCESS",
                    confirmation_result=confirmation_message,
                    errors=None
                )
                logger.info(f"Application {application_id} successfully submitted and verified!")

            else:
                # Require human review if confirmation indicator was not confidently detected
                app_record.status = "SUBMISSION_UNVERIFIED"
                app_record.browser_state = {
                    "status": "SUBMISSION_UNVERIFIED",
                    "current_step": "VERIFY_CONFIRMATION",
                    "last_successful_step": "CLICK_SUBMIT",
                    "error_code": "CONFIRMATION_NOT_DETECTED",
                    "error_message": "Submit clicked but no explicit confirmation notice or reference number was detected. Human review required.",
                    "submission_url": page.url,
                    "timestamp": datetime.utcnow().isoformat()
                }
                db.commit()

                cls.record_audit_log(
                    db=db,
                    application_id=app_record.id,
                    job_id=job.id,
                    url=page.url,
                    browser_action="FINAL_SUBMISSION",
                    fields_populated={f.name: f.value for f in filled},
                    files_uploaded=[tailored_cv.pdf_path] if tailored_cv and tailored_cv.pdf_path else [],
                    human_approval=True,
                    submission_result="UNVERIFIED",
                    confirmation_result=None,
                    errors="Confirmation message not detected on post-submit page."
                )
                logger.warning(f"Application {application_id} submit completed but status is SUBMISSION_UNVERIFIED.")

            return app_record.browser_state

        finally:
            browser_mgr.close()

    @classmethod
    def cancel_submission(
        cls,
        db: Session,
        application_id: str,
        reason: str = "Cancelled by candidate"
    ) -> Dict[str, Any]:
        """Cancels an in-progress or review-pending browser submission."""
        app_record = db.query(Application).filter(Application.id == application_id).first()
        if not app_record:
            raise ValueError(f"Application '{application_id}' not found.")

        app_record.submission_token = None
        app_record.submission_lock = False
        app_record.status = "READY_FOR_SUBMISSION"
        app_record.browser_state = {
            "status": "READY_FOR_SUBMISSION",
            "current_step": "CANCELLED",
            "last_successful_step": "CANCELLED",
            "error_message": f"Submission cancelled: {reason}",
            "timestamp": datetime.utcnow().isoformat()
        }
        db.commit()

        cls.record_audit_log(
            db=db,
            application_id=app_record.id,
            job_id=app_record.job_id,
            url=app_record.submission_url or "",
            browser_action="SUBMISSION_CANCELLED",
            fields_populated={},
            files_uploaded=[],
            human_approval=False,
            submission_result="CANCELLED",
            confirmation_result=None,
            errors=reason
        )
        return app_record.browser_state
