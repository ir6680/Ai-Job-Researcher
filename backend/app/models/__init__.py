"""
SQLAlchemy Models for Lahore AI Job Application Agent.
All 10 required database tables are declared with robust constraints and relationships.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    JSON,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from backend.app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    target_city = Column(String(100), default="Lahore")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    master_cvs = relationship("MasterCV", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


class MasterCV(Base):
    __tablename__ = "master_cv"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Personal Information
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), default="Lahore, Pakistan")
    summary = Column(Text, nullable=True)
    
    # Profiles & Links
    github_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)

    # Versioning & Audit
    version = Column(Integer, default=1)
    is_primary = Column(Boolean, default=True)
    raw_text = Column(Text, nullable=True)
    source_filename = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="master_cvs")
    skills = relationship("Skill", back_populates="master_cv", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="master_cv", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="master_cv", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="master_cv", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="master_cv", cascade="all, delete-orphan")
    tailored_cvs = relationship("TailoredCV", back_populates="master_cv", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="master_cv")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_cv_id = Column(String(36), ForeignKey("master_cv.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(100), nullable=False, index=True)
    # Category: Languages, Frameworks, Databases, Tools/DevOps, Soft Skills, Other
    category = Column(String(50), default="Technical")
    proficiency = Column(String(50), default="Intermediate") # Beginner, Intermediate, Expert
    years_of_experience = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    master_cv = relationship("MasterCV", back_populates="skills")


class Education(Base):
    __tablename__ = "education"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_cv_id = Column(String(36), ForeignKey("master_cv.id", ondelete="CASCADE"), nullable=False, index=True)

    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False)
    grade_or_gpa = Column(String(50), nullable=True)
    location = Column(String(100), default="Lahore, Pakistan")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    master_cv = relationship("MasterCV", back_populates="education")


class Experience(Base):
    __tablename__ = "experience"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_cv_id = Column(String(36), ForeignKey("master_cv.id", ondelete="CASCADE"), nullable=False, index=True)

    company_name = Column(String(255), nullable=False)
    role_title = Column(String(255), nullable=False)
    employment_type = Column(String(50), default="Full-time") # Internship, Full-time, Contract, Freelance
    location = Column(String(100), default="Lahore, Pakistan")
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    highlights = Column(JSON, default=list) # List of bullet points
    technologies_used = Column(JSON, default=list) # List of tech tools used
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    master_cv = relationship("MasterCV", back_populates="experience")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_cv_id = Column(String(36), ForeignKey("master_cv.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    role = Column(String(100), nullable=True)
    technologies = Column(JSON, default=list) # List of tools/tech
    repo_url = Column(String(500), nullable=True)
    live_url = Column(String(500), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    highlights = Column(JSON, default=list) # Key achievements
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    master_cv = relationship("MasterCV", back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_cv_id = Column(String(36), ForeignKey("master_cv.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=False)
    issue_date = Column(String(50), nullable=True)
    expiration_date = Column(String(50), nullable=True)
    credential_id = Column(String(100), nullable=True)
    credential_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    master_cv = relationship("MasterCV", back_populates="certifications")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company = Column(String(255), nullable=False, index=True)
    job_title = Column(String(255), nullable=False, index=True)
    location = Column(String(255), default="Lahore, Pakistan")
    job_url = Column(String(1000), nullable=True)
    source_url = Column(String(1000), nullable=True) # Canonical source URL
    description = Column(Text, nullable=False)
    raw_description = Column(Text, nullable=True) # Full unedited raw text
    responsibilities = Column(JSON, default=list) # List of key job duties
    
    # Requirements
    required_skills = Column(JSON, default=list) # List of required skills
    preferred_skills = Column(JSON, default=list) # List of preferred skills
    experience_requirement = Column(String(100), default="Entry-level (0-1 years)")
    education_requirement = Column(String(255), default="BS Computer Science / Software Engineering")
    job_type = Column(String(50), default="Full-time") # Full-time, Internship, Hybrid, Remote
    salary = Column(String(100), nullable=True)
    source = Column(String(100), default="Manual") # e.g. Systems Limited, Rozee.pk, Arbisoft, etc.
    status = Column(String(50), default="discovered") # discovered, saved, ignored, applied, archived
    job_status = Column(String(50), default="discovered", index=True) # Synced with status

    # Discovery & Deduplication metadata
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    posting_date = Column(String(50), nullable=True)
    deadline = Column(String(50), nullable=True)
    duplicate_status = Column(String(50), default="unique", index=True) # unique, duplicate
    canonical_job_id = Column(String(36), nullable=True) # Reference to canonical job if duplicate
    dedup_hash = Column(String(64), nullable=True, index=True) # SHA-256 fingerprint

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    tailored_cvs = relationship("TailoredCV", back_populates="job", cascade="all, delete-orphan")


class JobDiscoveryRun(Base):
    __tablename__ = "job_discovery_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="running") # running, completed, failed
    sources_checked = Column(JSON, default=list)
    keywords_used = Column(JSON, default=list)
    total_discovered = Column(Integer, default=0)
    new_jobs_added = Column(Integer, default=0)
    duplicates_skipped = Column(Integer, default=0)
    rejected_non_lahore = Column(Integer, default=0)
    rejected_non_entry = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    master_cv_id = Column(String(36), ForeignKey("master_cv.id", ondelete="CASCADE"), nullable=False)
    tailored_cv_id = Column(String(36), ForeignKey("tailored_cvs.id", ondelete="SET NULL"), nullable=True)
    match_result_id = Column(String(100), nullable=True)

    # Status: DRAFT, REVIEW_REQUIRED, READY_FOR_SUBMISSION, SUBMITTED, REJECTED, WITHDRAWN, INTERVIEW, OFFER
    status = Column(String(50), default="DRAFT", index=True)
    readiness_status = Column(String(50), default="REVIEW_REQUIRED") # READY, REVIEW_REQUIRED
    
    # Generated Application Package & Content
    cover_letter = Column(Text, nullable=True)
    candidate_profile = Column(JSON, default=dict)
    application_fields = Column(JSON, default=dict)
    application_answers = Column(JSON, default=dict)
    application_package = Column(JSON, default=dict)
    user_edits = Column(JSON, default=dict)
    validation_errors = Column(JSON, default=list)
    evidence_map = Column(JSON, default=list)

    applied_at = Column(DateTime, nullable=True)
    interview_date = Column(DateTime, nullable=True)
    review_timestamp = Column(DateTime, nullable=True)
    approval_timestamp = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # Phase 6 Controlled Browser Agent Fields
    browser_state = Column(JSON, default=dict)
    submission_lock = Column(Boolean, default=False)
    submission_token = Column(String(100), nullable=True)
    submission_attempt_id = Column(String(100), nullable=True)
    confirmation_message = Column(Text, nullable=True)
    confirmation_reference = Column(String(255), nullable=True)
    submission_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    master_cv = relationship("MasterCV", back_populates="applications")
    tailored_cv = relationship("TailoredCV", back_populates="applications")
    packages = relationship("ApplicationPackage", back_populates="application", cascade="all, delete-orphan")
    answers = relationship("ApplicationAnswer", back_populates="application", cascade="all, delete-orphan")
    reviews = relationship("ApplicationReview", back_populates="application", cascade="all, delete-orphan")
    audit_logs = relationship("SubmissionAuditLog", back_populates="application", cascade="all, delete-orphan")


class ApplicationPackage(Base):
    __tablename__ = "application_packages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    match_result_id = Column(String(100), nullable=True)
    tailored_cv_id = Column(String(36), ForeignKey("tailored_cvs.id", ondelete="SET NULL"), nullable=True)
    cover_letter = Column(Text, nullable=True)
    candidate_profile = Column(JSON, default=dict)
    application_fields = Column(JSON, default=dict)
    readiness_status = Column(String(50), default="REVIEW_REQUIRED")
    validation_errors = Column(JSON, default=list)
    evidence_map = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    application = relationship("Application", back_populates="packages")


class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    question_key = Column(String(100), nullable=False)
    question_text = Column(String(500), nullable=False)
    answer_text = Column(Text, nullable=True)
    status = Column(String(50), default="REQUIRES_USER_INPUT") # AUTO_ANSWERED, REQUIRES_USER_INPUT, USER_EDITED
    source_evidence = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    application = relationship("Application", back_populates="answers")


class ApplicationReview(Base):
    __tablename__ = "application_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_name = Column(String(255), default="Candidate")
    decision = Column(String(50), nullable=False) # APPROVED, REJECTED, CHANGES_REQUESTED
    notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    application = relationship("Application", back_populates="reviews")


class TailoredCV(Base):
    __tablename__ = "tailored_cvs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_cv_id = Column(String(36), ForeignKey("master_cv.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    match_result_id = Column(String(100), nullable=True)
    version = Column(Integer, default=1)

    target_company = Column(String(255), nullable=True)
    target_role = Column(String(255), nullable=True)
    match_score = Column(Float, nullable=True)
    ats_keyword_coverage = Column(Float, nullable=True) # e.g. 82.0 (%)
    integrity_status = Column(String(50), default="PASS") # PASS or REVIEW_REQUIRED
    human_reviewed = Column(Boolean, default=False)

    # Detailed structured artifacts
    structured_content = Column(JSON, default=dict) # Complete tailored CV sections
    tailoring_changes = Column(JSON, default=dict) # Summary of sections reordered, skills prioritized, bullets rewritten
    evidence_map = Column(JSON, default=list) # List of {"generated_text", "source_section", "source_item", "source_text", "reason"}
    rejected_claims = Column(JSON, default=list) # List of claims blocked by hallucination guard
    matched_keywords = Column(JSON, default=list)
    missing_keywords = Column(JSON, default=list)

    # File exports
    docx_path = Column(String(500), nullable=True)
    pdf_path = Column(String(500), nullable=True)

    # Deterministic caching fingerprint
    cache_hash = Column(String(64), nullable=True, index=True)

    # Backward compatibility
    tailored_content = Column(JSON, default=dict)
    highlighted_skills = Column(JSON, default=list)

    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    master_cv = relationship("MasterCV", back_populates="tailored_cvs")
    job = relationship("Job", back_populates="tailored_cvs")
    applications = relationship("Application", back_populates="tailored_cv")


class SubmissionAuditLog(Base):
    """
    Immutable audit record for every submission attempt or browser action.
    Never stores sensitive passwords or OTP codes.
    """
    __tablename__ = "submission_audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    url = Column(String(500), nullable=False)
    browser_action = Column(String(100), nullable=False)  # DRY_RUN, FORM_FILL, FINAL_SUBMISSION, CANCELLED
    fields_populated = Column(JSON, default=dict)
    files_uploaded = Column(JSON, default=list)
    human_approval = Column(Boolean, default=False)
    submission_result = Column(String(50), nullable=False)  # SUCCESS, FAILED, BLOCKED, DRY_RUN_COMPLETE, UNVERIFIED
    confirmation_result = Column(String(255), nullable=True)
    errors = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    application = relationship("Application", back_populates="audit_logs")
    job = relationship("Job")

