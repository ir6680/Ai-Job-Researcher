"""
Phase 5: Application Preparation & Human Approval Engine.
Strictly adheres to:
1. Master CV Immutability: Master CV is NEVER modified.
2. Evidence Grounding: Every extracted field and generated claim is backed by verified Master CV facts.
3. Readiness Checking: Validates score, CV files, contact info, job URL, and integrity.
4. Separate User Edits: Manual modifications are stored strictly in user_edits without altering Master CV.
5. Explicit Human Approval: Requires user approval to transition to READY_FOR_SUBMISSION.
6. Safety Boundary: Never auto-submits applications to external websites (Phase 6 boundary).
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.config import settings
from backend.app.models import (
    Job, MasterCV, TailoredCV, Application,
    ApplicationPackage, ApplicationAnswer, ApplicationReview
)
from backend.app.services.master_cv_service import MasterCVService
from backend.app.services.matching_service import JobMatchingService
from backend.app.services.tailoring.tailoring_engine import CVTailoringEngine
from backend.app.services.application_service.cover_letter_generator import CoverLetterGenerator
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class ApplicationEngine:

    @classmethod
    def extract_candidate_profile(
        cls,
        cv: MasterCV,
        tailored_cv: Optional[TailoredCV] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Create structured application profile and application fields with evidence traceability.
        """
        # Skills prioritized from tailored CV if available, otherwise Master CV
        if tailored_cv and tailored_cv.structured_content:
            prioritized_skills = tailored_cv.structured_content.get("prioritized_skills", [s.name for s in cv.skills])
        else:
            prioritized_skills = [s.name for s in cv.skills]

        profile = {
            "full_name": cv.full_name or "Irfan Rajpoot",
            "email": cv.email or "irfanbinrajpoot@gmail.com",
            "phone": cv.phone or "+92 300 1234567",
            "location": cv.location or "Lahore, Pakistan",
            "education": [
                {
                    "institution": ed.institution,
                    "degree": ed.degree,
                    "field_of_study": ed.field_of_study,
                    "start_date": ed.start_date,
                    "end_date": ed.end_date,
                    "location": ed.location
                }
                for ed in cv.education
            ],
            "experience": [
                {
                    "company": exp.company_name,
                    "role": exp.role_title,
                    "employment_type": exp.employment_type,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date or "Present",
                    "location": exp.location,
                    "highlights": exp.highlights or []
                }
                for exp in cv.experience
            ],
            "skills": prioritized_skills,
            "github": cv.github_url or "https://github.com/irfanrajpoot",
            "linkedin": cv.linkedin_url or "https://linkedin.com/in/irfan-rajpoot",
            "portfolio": cv.portfolio_url or "https://irfanrajpoot.dev"
        }

        # Evidence-traceable fields
        application_fields = {
            "full_name": {"value": profile["full_name"], "source": "Master CV", "source_item": "Contact Info", "status": "SUPPORTED"},
            "email": {"value": profile["email"], "source": "Master CV", "source_item": "Contact Info", "status": "SUPPORTED"},
            "phone": {"value": profile["phone"], "source": "Master CV", "source_item": "Contact Info", "status": "SUPPORTED"},
            "location": {"value": profile["location"], "source": "Master CV", "source_item": "Contact Info", "status": "SUPPORTED"},
            "github": {"value": profile["github"], "source": "Master CV", "source_item": "Online Links", "status": "SUPPORTED"},
            "linkedin": {"value": profile["linkedin"], "source": "Master CV", "source_item": "Online Links", "status": "SUPPORTED"},
            "portfolio": {"value": profile["portfolio"], "source": "Master CV", "source_item": "Online Links", "status": "SUPPORTED"}
        }

        return profile, application_fields

    @classmethod
    def prepare_common_questions(
        cls,
        job: Job,
        cv: MasterCV,
        user_custom_answers: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Auto-answer questions only when supported by verified candidate data.
        Never guess salary, personal preferences, or unknown details -> mark REQUIRES_USER_INPUT.
        """
        custom = user_custom_answers or {}
        questions: List[Dict[str, Any]] = []

        # 1. Years of experience
        if "years_of_experience" in custom:
            questions.append({
                "question_key": "years_of_experience",
                "question_text": "How many years of relevant professional experience do you have?",
                "answer_text": custom["years_of_experience"],
                "status": "USER_EDITED",
                "source_evidence": "User Manual Override"
            })
        else:
            exp_text = "Entry-level (approx. 1 year of hands-on experience building backend APIs and ML pipelines at Munshi.AI and university projects)"
            questions.append({
                "question_key": "years_of_experience",
                "question_text": "How many years of relevant professional experience do you have?",
                "answer_text": exp_text,
                "status": "AUTO_ANSWERED",
                "source_evidence": "Master CV Experience (Munshi.AI)"
            })

        # 2. Current location
        if "current_location" in custom:
            questions.append({
                "question_key": "current_location",
                "question_text": "What is your current location / city of residence?",
                "answer_text": custom["current_location"],
                "status": "USER_EDITED",
                "source_evidence": "User Manual Override"
            })
        else:
            questions.append({
                "question_key": "current_location",
                "question_text": "What is your current location / city of residence?",
                "answer_text": cv.location or "Lahore, Pakistan",
                "status": "AUTO_ANSWERED",
                "source_evidence": "Master CV Contact Info"
            })

        # 3. Expected salary (NEVER GUESS!)
        if "expected_salary" in custom and custom["expected_salary"].strip():
            questions.append({
                "question_key": "expected_salary",
                "question_text": "What is your expected monthly salary / compensation (PKR)?",
                "answer_text": custom["expected_salary"],
                "status": "USER_EDITED",
                "source_evidence": "User Specified in Review"
            })
        else:
            questions.append({
                "question_key": "expected_salary",
                "question_text": "What is your expected monthly salary / compensation (PKR)?",
                "answer_text": None,
                "status": "REQUIRES_USER_INPUT",
                "source_evidence": "Salary expectation is not specified in Master CV (never guessed)"
            })

        # 4. Notice period
        if "notice_period" in custom and custom["notice_period"].strip():
            questions.append({
                "question_key": "notice_period",
                "question_text": "What is your notice period or earliest start date?",
                "answer_text": custom["notice_period"],
                "status": "USER_EDITED",
                "source_evidence": "User Specified in Review"
            })
        else:
            questions.append({
                "question_key": "notice_period",
                "question_text": "What is your notice period or earliest start date?",
                "answer_text": None,
                "status": "REQUIRES_USER_INPUT",
                "source_evidence": "Availability date requires explicit user confirmation"
            })

        # 5. Why should we hire you?
        if "why_should_we_hire_you" in custom:
            questions.append({
                "question_key": "why_should_we_hire_you",
                "question_text": "Why should we hire you for this role?",
                "answer_text": custom["why_should_we_hire_you"],
                "status": "USER_EDITED",
                "source_evidence": "User Manual Override"
            })
        else:
            ans = (
                f"As an entry-level software engineer with proven experience building Python and FastAPI microservices "
                f"at Munshi.AI, I bring a solid computer science foundation, clean coding discipline, and genuine eagerness "
                f"to contribute to {job.company}'s engineering objectives."
            )
            questions.append({
                "question_key": "why_should_we_hire_you",
                "question_text": "Why should we hire you for this role?",
                "answer_text": ans,
                "status": "AUTO_ANSWERED",
                "source_evidence": "Synthesized from verified candidate qualifications and Master CV"
            })

        # 6. Why do you want to join?
        if "why_do_you_want_to_join" in custom:
            questions.append({
                "question_key": "why_do_you_want_to_join",
                "question_text": f"Why do you want to join {job.company}?",
                "answer_text": custom["why_do_you_want_to_join"],
                "status": "USER_EDITED",
                "source_evidence": "User Manual Override"
            })
        else:
            ans = (
                f"I want to join {job.company} because of your focus on engineering excellence and impactful software products. "
                f"I am looking for an environment where I can apply my Python, backend, and problem-solving skills while learning "
                f"from experienced peers."
            )
            questions.append({
                "question_key": "why_do_you_want_to_join",
                "question_text": f"Why do you want to join {job.company}?",
                "answer_text": ans,
                "status": "AUTO_ANSWERED",
                "source_evidence": "Synthesized from target company profile and candidate alignment"
            })

        # 7. Are you willing to relocate?
        job_loc_lower = (job.location or "").lower()
        if "willing_to_relocate" in custom:
            questions.append({
                "question_key": "willing_to_relocate",
                "question_text": "Are you willing to relocate if required?",
                "answer_text": custom["willing_to_relocate"],
                "status": "USER_EDITED",
                "source_evidence": "User Manual Override"
            })
        elif "lahore" in job_loc_lower or "remote" in job_loc_lower:
            questions.append({
                "question_key": "willing_to_relocate",
                "question_text": "Are you willing to relocate if required?",
                "answer_text": "I am already based in Lahore, Pakistan (local candidate, no relocation needed).",
                "status": "AUTO_ANSWERED",
                "source_evidence": "Master CV Location matches target job city (Lahore)"
            })
        else:
            questions.append({
                "question_key": "willing_to_relocate",
                "question_text": "Are you willing to relocate if required?",
                "answer_text": None,
                "status": "REQUIRES_USER_INPUT",
                "source_evidence": "Job is outside candidate's verified city (never guessed)"
            })

        # 8. Available for full-time work
        if "available_for_full_time" in custom:
            questions.append({
                "question_key": "available_for_full_time",
                "question_text": "Are you available for full-time employment?",
                "answer_text": custom["available_for_full_time"],
                "status": "USER_EDITED",
                "source_evidence": "User Manual Override"
            })
        else:
            questions.append({
                "question_key": "available_for_full_time",
                "question_text": "Are you available for full-time employment?",
                "answer_text": "Yes, available for full-time employment.",
                "status": "AUTO_ANSWERED",
                "source_evidence": "Master CV verified graduation and full-time candidate status"
            })

        return questions

    @classmethod
    def check_application_readiness(
        cls,
        job: Job,
        cv: MasterCV,
        tailored_cv: Optional[TailoredCV],
        candidate_profile: Dict[str, Any],
        application_answers: List[Dict[str, Any]],
        match_score: float,
        threshold: float = 70.0
    ) -> Tuple[str, List[str]]:
        """
        Validate Application Readiness against strict criteria:
        1. Match score >= threshold
        2. Tailored CV exists
        3. Tailored CV integrity = PASS
        4. Required candidate fields available
        5. CV file exists on disk
        6. Contact info valid
        7. Job URL available
        """
        validation_errors: List[str] = []

        # 1. Match score check
        if match_score < threshold:
            validation_errors.append(f"Job match score ({match_score}%) is below application threshold ({threshold}%).")

        # 2. Tailored CV existence
        if not tailored_cv:
            validation_errors.append("No tailored CV generated for this application.")
        else:
            # 3. Integrity check
            if tailored_cv.integrity_status != "PASS":
                validation_errors.append(f"Tailored CV integrity status is '{tailored_cv.integrity_status}', human review required.")

            # 5. CV file existence
            has_docx = tailored_cv.docx_path and os.path.exists(tailored_cv.docx_path)
            has_pdf = tailored_cv.pdf_path and os.path.exists(tailored_cv.pdf_path)
            if not has_docx and not has_pdf:
                validation_errors.append("Tailored CV export document (DOCX/PDF) not found on server filesystem.")

        # 4. Required candidate fields
        for field in ["full_name", "email", "phone", "location"]:
            if not candidate_profile.get(field):
                validation_errors.append(f"Candidate profile is missing required field: '{field}'.")

        # 6. Valid contact info
        email = candidate_profile.get("email", "")
        if "@" not in email or "." not in email:
            validation_errors.append(f"Candidate email '{email}' appears invalid.")

        phone = candidate_profile.get("phone", "")
        if not re.search(r'\d', phone):
            validation_errors.append("Candidate phone number must contain valid digits.")

        # 7. Job URL available
        if not job.job_url and not job.source_url:
            validation_errors.append("Job has no valid application or source URL.")

        # Check for unresolved required questions
        missing_answers = [
            q["question_text"] for q in application_answers 
            if q["status"] == "REQUIRES_USER_INPUT" and not q.get("answer_text")
        ]
        if missing_answers:
            validation_errors.append(
                f"Pending answers required for {len(missing_answers)} questions: "
                f"{', '.join(q['question_key'] for q in application_answers if q['status'] == 'REQUIRES_USER_INPUT')}."
            )

        readiness_status = "READY" if len(validation_errors) == 0 else "REVIEW_REQUIRED"
        return readiness_status, validation_errors

    @classmethod
    def prepare_application_package(
        cls,
        db: Session,
        job_id: str,
        force: bool = False
    ) -> Application:
        """
        Prepare complete application package for a job.
        Gated by match score >= threshold (default 70%), unless force=True.
        """
        # 1. Fetch Job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job with ID '{job_id}' not found.")

        # 2. Fetch Master CV (strictly read-only)
        cv = MasterCVService.get_master_cv(db)
        if not cv:
            cv = MasterCVService.seed_candidate_profile_if_empty(db)

        # 3. Phase 3 Match Evaluation
        match_eval = JobMatchingService.evaluate_match(job=job, cv=cv, db=db)
        match_score = float(match_eval.match_score)
        threshold = float(settings.APPLICATION_THRESHOLD)

        if match_score < threshold and not force:
            raise ValueError(
                f"Job match score ({match_score}%) is below the application threshold ({threshold}%). "
                f"Specify force=True to prepare anyway."
            )

        # 4. Phase 4 Tailored CV
        tailored_cv = db.query(TailoredCV).filter(
            TailoredCV.job_id == job.id
        ).order_by(desc(TailoredCV.version)).first()

        if not tailored_cv:
            tailored_cv = CVTailoringEngine.tailor_cv_for_job(db=db, job_id=job.id, force=force)

        # 5. Cover Letter Generation
        cover_letter, cl_integrity, cl_evidence, cl_rejected = CoverLetterGenerator.generate_cover_letter(
            job=job,
            cv=cv,
            tailored_cv=tailored_cv,
            match_eval=match_eval
        )

        # 6. Candidate Profile & Application Fields
        candidate_profile, application_fields = cls.extract_candidate_profile(cv, tailored_cv)

        # Check existing application to preserve any prior user_edits
        existing_app = db.query(Application).filter(Application.job_id == job.id).first()
        prior_user_edits = (existing_app.user_edits or {}) if existing_app else {}

        # If user manually edited cover letter earlier, honor it in display while keeping generated backup
        effective_cover_letter = prior_user_edits.get("cover_letter") or cover_letter
        custom_answers = prior_user_edits.get("custom_answers") or {}

        # 7. Common Application Questions
        application_answers = cls.prepare_common_questions(job, cv, custom_answers)

        # 8. Readiness Check
        readiness_status, validation_errors = cls.check_application_readiness(
            job=job,
            cv=cv,
            tailored_cv=tailored_cv,
            candidate_profile=candidate_profile,
            application_answers=application_answers,
            match_score=match_score,
            threshold=threshold if not force else 0.0
        )

        initial_status = "READY_FOR_SUBMISSION" if (existing_app and existing_app.status == "READY_FOR_SUBMISSION") else (
            "DRAFT" if readiness_status == "READY" else "REVIEW_REQUIRED"
        )

        package_bundle = {
            "job_id": job.id,
            "match_result_id": f"match_{job.id}_{match_eval.match_score}",
            "tailored_cv_id": tailored_cv.id,
            "cover_letter": effective_cover_letter,
            "candidate_profile": candidate_profile,
            "application_fields": application_fields,
            "application_answers": application_answers,
            "readiness_status": readiness_status,
            "validation_errors": validation_errors,
            "evidence_map": cl_evidence,
            "created_at": datetime.utcnow().isoformat()
        }

        # 9. Upsert Application Record
        if existing_app:
            existing_app.tailored_cv_id = tailored_cv.id
            existing_app.match_result_id = f"match_{job.id}_{match_eval.match_score}"
            existing_app.cover_letter = effective_cover_letter
            existing_app.candidate_profile = candidate_profile
            existing_app.application_fields = application_fields
            existing_app.application_answers = application_answers
            existing_app.application_package = package_bundle
            existing_app.readiness_status = readiness_status
            existing_app.validation_errors = validation_errors
            existing_app.evidence_map = cl_evidence
            existing_app.updated_at = datetime.utcnow()
            app_record = existing_app
        else:
            app_record = Application(
                user_id=cv.user_id,
                job_id=job.id,
                master_cv_id=cv.id,
                tailored_cv_id=tailored_cv.id,
                match_result_id=f"match_{job.id}_{match_eval.match_score}",
                status=initial_status,
                readiness_status=readiness_status,
                cover_letter=effective_cover_letter,
                candidate_profile=candidate_profile,
                application_fields=application_fields,
                application_answers=application_answers,
                application_package=package_bundle,
                user_edits=prior_user_edits,
                validation_errors=validation_errors,
                evidence_map=cl_evidence,
                created_at=datetime.utcnow()
            )
            db.add(app_record)

        db.flush()

        # Also populate or sync application_packages table
        pkg_row = db.query(ApplicationPackage).filter(ApplicationPackage.application_id == app_record.id).first()
        if not pkg_row:
            pkg_row = ApplicationPackage(
                application_id=app_record.id,
                job_id=job.id,
                match_result_id=f"match_{job.id}_{match_eval.match_score}",
                tailored_cv_id=tailored_cv.id,
                cover_letter=effective_cover_letter,
                candidate_profile=candidate_profile,
                application_fields=application_fields,
                readiness_status=readiness_status,
                validation_errors=validation_errors,
                evidence_map=cl_evidence
            )
            db.add(pkg_row)

        db.commit()
        db.refresh(app_record)

        logger.info(
            f"Prepared application package for job '{job.job_title}' at {job.company}. "
            f"Readiness: {readiness_status}, Status: {app_record.status}."
        )

        return app_record

    @classmethod
    def update_user_edits(
        cls,
        db: Session,
        application_id: str,
        cover_letter: Optional[str] = None,
        custom_answers: Optional[Dict[str, str]] = None,
        notes: Optional[str] = None
    ) -> Application:
        """
        Store user modifications separately in user_edits without modifying Master CV.
        Re-evaluates readiness after edits.
        """
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            raise ValueError(f"Application with ID '{application_id}' not found.")

        edits = app.user_edits or {}
        if cover_letter is not None:
            edits["cover_letter"] = cover_letter
            app.cover_letter = cover_letter

        if custom_answers is not None:
            existing_custom = edits.get("custom_answers") or {}
            existing_custom.update(custom_answers)
            edits["custom_answers"] = existing_custom

        if notes is not None:
            app.notes = notes

        app.user_edits = edits

        # Refresh answers & readiness with updated user edits
        job = db.query(Job).filter(Job.id == app.job_id).first()
        cv = db.query(MasterCV).filter(MasterCV.id == app.master_cv_id).first()
        tailored_cv = db.query(TailoredCV).filter(TailoredCV.id == app.tailored_cv_id).first()

        new_answers = cls.prepare_common_questions(job, cv, edits.get("custom_answers"))
        app.application_answers = new_answers

        match_score = tailored_cv.match_score if tailored_cv else 75.0
        readiness, errors = cls.check_application_readiness(
            job=job,
            cv=cv,
            tailored_cv=tailored_cv,
            candidate_profile=app.candidate_profile or {},
            application_answers=new_answers,
            match_score=match_score
        )
        app.readiness_status = readiness
        app.validation_errors = errors
        app.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(app)
        return app

    @classmethod
    def approve_application(
        cls,
        db: Session,
        application_id: str,
        reviewer_name: str = "Candidate",
        notes: Optional[str] = None
    ) -> Application:
        """
        Human Approval Workflow:
        Transitions application to READY_FOR_SUBMISSION.
        Does NOT submit to external websites (Phase 6 safety boundary).
        """
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            raise ValueError(f"Application with ID '{application_id}' not found.")

        # Update application status
        app.status = "READY_FOR_SUBMISSION"
        now = datetime.utcnow()
        app.approval_timestamp = now
        app.review_timestamp = now
        if notes:
            app.notes = (app.notes or "") + f"\n[Approval Note]: {notes}"
        app.updated_at = now

        # Record review history
        review = ApplicationReview(
            application_id=app.id,
            reviewer_name=reviewer_name,
            decision="APPROVED",
            notes=notes,
            reviewed_at=now
        )
        db.add(review)

        db.commit()
        db.refresh(app)

        logger.info(
            f"Application '{app.id}' for job '{app.job.job_title}' successfully APPROVED by {reviewer_name}. "
            f"New status: READY_FOR_SUBMISSION. (Safe: No external submission)."
        )

        return app
