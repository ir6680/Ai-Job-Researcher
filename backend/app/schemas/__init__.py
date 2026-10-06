"""
Pydantic Schemas for Request Validation and Response Serialization.
Strict typing with Pydantic v2.
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict


# ==========================================
# Common & User Schemas
# ==========================================

class UserBase(BaseModel):
    email: str
    full_name: str
    target_city: str = "Lahore"


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Skills Schemas
# ==========================================

class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(default="Technical", description="e.g. Languages, Frameworks, Databases, Tools/DevOps, Soft Skills")
    proficiency: str = Field(default="Intermediate", description="Beginner, Intermediate, or Expert")
    years_of_experience: Optional[float] = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_of_experience: Optional[float] = None


class SkillResponse(SkillBase):
    id: str
    master_cv_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Education Schemas
# ==========================================

class EducationBase(BaseModel):
    institution: str = Field(..., min_length=1, max_length=255)
    degree: str = Field(..., min_length=1, max_length=255)
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    grade_or_gpa: Optional[str] = None
    location: Optional[str] = "Lahore, Pakistan"
    description: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    grade_or_gpa: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class EducationResponse(EducationBase):
    id: str
    master_cv_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Experience Schemas
# ==========================================

class ExperienceBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    role_title: str = Field(..., min_length=1, max_length=255)
    employment_type: str = Field(default="Full-time", description="Full-time, Internship, Contract, Freelance")
    location: Optional[str] = "Lahore, Pakistan"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)
    technologies_used: list[str] = Field(default_factory=list)


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    highlights: Optional[list[str]] = None
    technologies_used: Optional[list[str]] = None


class ExperienceResponse(ExperienceBase):
    id: str
    master_cv_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Projects Schemas
# ==========================================

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    role: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    technologies: Optional[list[str]] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    highlights: Optional[list[str]] = None


class ProjectResponse(ProjectBase):
    id: str
    master_cv_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Certifications Schemas
# ==========================================

class CertificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    issuing_organization: str = Field(..., min_length=1, max_length=255)
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationResponse(CertificationBase):
    id: str
    master_cv_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Master CV Schemas
# ==========================================

class MasterCVBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = "Lahore, Pakistan"
    summary: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None
    is_primary: bool = True


class MasterCVCreate(MasterCVBase):
    user_id: Optional[str] = None
    skills: list[SkillCreate] = Field(default_factory=list)
    education: list[EducationCreate] = Field(default_factory=list)
    experience: list[ExperienceCreate] = Field(default_factory=list)
    projects: list[ProjectCreate] = Field(default_factory=list)
    certifications: list[CertificationCreate] = Field(default_factory=list)
    raw_text: Optional[str] = None
    source_filename: Optional[str] = None


class MasterCVUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None
    is_primary: Optional[bool] = None


class MasterCVResponse(MasterCVBase):
    id: str
    user_id: str
    version: int
    source_filename: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MasterCVFullResponse(MasterCVResponse):
    skills: list[SkillResponse] = []
    education: list[EducationResponse] = []
    experience: list[ExperienceResponse] = []
    projects: list[ProjectResponse] = []
    certifications: list[CertificationResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Parsed CV Extracted Schema (Never Inventions)
# ==========================================

class ExtractedCVData(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None
    
    skills: list[SkillCreate] = Field(default_factory=list)
    education: list[EducationCreate] = Field(default_factory=list)
    experience: list[ExperienceCreate] = Field(default_factory=list)
    projects: list[ProjectCreate] = Field(default_factory=list)
    certifications: list[CertificationCreate] = Field(default_factory=list)
    tools_and_technologies: list[str] = Field(default_factory=list)
    
    raw_text: str = ""
    filename: str = ""
    extraction_notes: list[str] = Field(default_factory=list)


# ==========================================
# Job Data Model Schemas (Phase 2 Extended)
# ==========================================

class JobBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=255, description="e.g. Systems Limited, Arbisoft, Devsinc")
    job_title: str = Field(..., min_length=1, max_length=255, description="e.g. Associate Software Engineer, Junior Python Developer")
    location: str = Field(default="Lahore, Pakistan")
    job_url: Optional[str] = None
    source_url: Optional[str] = None
    description: str = Field(..., min_length=10)
    raw_description: Optional[str] = None
    responsibilities: list[str] = Field(default_factory=list)
    
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_requirement: str = Field(default="Entry-level (0-1 years)")
    education_requirement: str = Field(default="BS Computer Science / Software Engineering or equivalent")
    job_type: str = Field(default="Full-time", description="Full-time, Internship, Hybrid, Remote")
    salary: Optional[str] = Field(default=None, description="e.g. PKR 70,000 - 120,000 / month")
    source: str = Field(default="Manual", description="e.g. Systems Limited, Rozee.pk, Careers Portal")
    status: str = Field(default="discovered", description="discovered, saved, ignored, applied, archived")
    job_status: str = Field(default="discovered", description="discovered, saved, ignored, applied, archived")
    
    # Discovery metadata
    posting_date: Optional[str] = None
    deadline: Optional[str] = None
    duplicate_status: str = Field(default="unique", description="unique, duplicate")
    canonical_job_id: Optional[str] = None
    dedup_hash: Optional[str] = None
    notes: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None
    source_url: Optional[str] = None
    description: Optional[str] = None
    raw_description: Optional[str] = None
    responsibilities: Optional[list[str]] = None
    required_skills: Optional[list[str]] = None
    preferred_skills: Optional[list[str]] = None
    experience_requirement: Optional[str] = None
    education_requirement: Optional[str] = None
    job_type: Optional[str] = None
    salary: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    job_status: Optional[str] = None
    duplicate_status: Optional[str] = None
    posting_date: Optional[str] = None
    deadline: Optional[str] = None
    notes: Optional[str] = None


class JobStatusUpdate(BaseModel):
    status: str = Field(..., description="saved, ignored, applied, archived, discovered")


class JobResponse(JobBase):
    id: str
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobDiscoveryRunRequest(BaseModel):
    keywords: Optional[list[str]] = None
    sources: Optional[list[str]] = None
    target_city: Optional[str] = "Lahore"
    target_country: Optional[str] = "Pakistan"
    max_jobs_per_run: Optional[int] = Field(default=50, ge=1, le=200)
    force_refresh: bool = False


class JobDiscoveryRunResponse(BaseModel):
    id: str
    triggered_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    sources_checked: list[str] = []
    keywords_used: list[str] = []
    total_discovered: int = 0
    new_jobs_added: int = 0
    duplicates_skipped: int = 0
    rejected_non_lahore: int = 0
    rejected_non_entry: int = 0
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobDiscoverySourceInfo(BaseModel):
    id: str
    name: str
    type: str # company_careers, job_board, search_engine
    is_active: bool
    base_url: str
    description: str


# ==========================================
# Application Schemas
# ==========================================

class ApplicationBase(BaseModel):
    job_id: str
    master_cv_id: str
    status: str = Field(default="draft", description="draft, ready, applied, screening, interview, offered, rejected, withdrawn")
    applied_at: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    user_id: Optional[str] = None
    tailored_cv_id: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    applied_at: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None
    tailored_cv_id: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: str
    user_id: str
    tailored_cv_id: Optional[str] = None
    match_result_id: Optional[str] = None
    readiness_status: str = "REVIEW_REQUIRED" # READY or REVIEW_REQUIRED
    cover_letter: Optional[str] = None
    candidate_profile: dict[str, Any] = Field(default_factory=dict)
    application_fields: dict[str, Any] = Field(default_factory=dict)
    application_answers: list[dict[str, Any]] = Field(default_factory=list)
    application_package: dict[str, Any] = Field(default_factory=dict)
    user_edits: dict[str, Any] = Field(default_factory=dict)
    validation_errors: list[str] = Field(default_factory=list)
    evidence_map: list[dict[str, Any]] = Field(default_factory=list)
    review_timestamp: Optional[datetime] = None
    approval_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Nested relations when populated
    job: Optional[JobResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Phase 5: Application Preparation & Human Approval Schemas
# ==========================================

class ApplicationQuestionAnswer(BaseModel):
    question_key: str
    question_text: str
    answer_text: Optional[str] = None
    status: str = Field(default="REQUIRES_USER_INPUT", description="AUTO_ANSWERED, REQUIRES_USER_INPUT, USER_EDITED")
    source_evidence: Optional[str] = None


class PrepareApplicationRequest(BaseModel):
    force: bool = Field(default=False, description="Manual override to prepare even if match score < 70%")


class ApplicationPackageResponse(BaseModel):
    job_id: str
    match_result_id: Optional[str] = None
    tailored_cv_id: Optional[str] = None
    cover_letter: str
    candidate_profile: dict[str, Any] = Field(default_factory=dict)
    application_fields: dict[str, Any] = Field(default_factory=dict)
    application_answers: list[ApplicationQuestionAnswer] = Field(default_factory=list)
    readiness_status: str = "REVIEW_REQUIRED" # READY or REVIEW_REQUIRED
    validation_errors: list[str] = Field(default_factory=list)
    evidence_map: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApplicationUpdatePayload(BaseModel):
    cover_letter: Optional[str] = None
    custom_answers: Optional[dict[str, str]] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    interview_date: Optional[datetime] = None


class ApplicationApprovalRequest(BaseModel):
    notes: Optional[str] = None
    reviewer_name: Optional[str] = "Candidate"


class CoverLetterResponse(BaseModel):
    application_id: Optional[str] = None
    job_id: str
    company: str
    job_title: str
    cover_letter: str
    integrity_status: str = "PASS"
    evidence_map: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# Phase 3: Job Matching & Candidate Fit Evaluation
# ==========================================

class JobMatchEvaluationResponse(BaseModel):
    job_id: str
    job_title: str
    company: str
    location: str
    match_score: int  # e.g. 87 (out of 100)
    match_score_decimal: float  # e.g. 0.87
    recommendation: str  # STRONG MATCH, GOOD MATCH, MODERATE MATCH, WEAK MATCH
    required_skills: List[str] = Field(default_factory=list, description="Matched required skills (✓)")
    relevant_experience: List[str] = Field(default_factory=list, description="Relevant experience & projects (✓)")
    partial: List[str] = Field(default_factory=list, description="Partial / adjacent skill matches (△)")
    missing: List[str] = Field(default_factory=list, description="Missing requirements or experience gaps (✗)")
    formatted_report: str = Field(..., description="Clean formatted text report matching the standard presentation")


# ==========================================
# Phase 4: Job-Specific CV Tailoring Schemas
# ==========================================

class EvidenceItem(BaseModel):
    generated_text: str
    source_section: str # summary, skills, experience, projects, education
    source_item: str # e.g. "Munshi.AI", "AI/ML FYP", "Master CV Summary"
    source_text: str
    reason: str


class TailoringChanges(BaseModel):
    sections_reordered: List[str] = Field(default_factory=list)
    skills_prioritized: List[str] = Field(default_factory=list)
    projects_prioritized: List[str] = Field(default_factory=list)
    rewritten_bullets_count: int = 0
    unsupported_claims_rejected: List[str] = Field(default_factory=list)


class ATSKeywordDetail(BaseModel):
    keyword: str
    status: str # SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED
    found_in_master_cv: bool


class TailoringRequest(BaseModel):
    force: bool = Field(default=False, description="Manual override if job match score < 70%")
    force_regenerate: bool = Field(default=False, description="Bypass cache and generate fresh version")


class TailoredCVResponse(BaseModel):
    id: str
    master_cv_id: str
    job_id: str
    version: int
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    match_score: Optional[float] = None
    ats_keyword_coverage: Optional[float] = None
    integrity_status: str = "PASS"
    human_reviewed: bool = False

    structured_content: dict[str, Any] = Field(default_factory=dict)
    tailoring_changes: dict[str, Any] = Field(default_factory=dict)
    evidence_map: List[dict[str, Any]] = Field(default_factory=list)
    rejected_claims: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)

    docx_path: Optional[str] = None
    pdf_path: Optional[str] = None
    docx_download_url: Optional[str] = None
    pdf_download_url: Optional[str] = None

    # Backward compatibility
    tailored_content: Optional[dict[str, Any]] = None
    highlighted_skills: Optional[list[str]] = None

    generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Phase 6: Browser Automation & Controlled Submission Schemas
# ==========================================

class BrowserPrepareRequest(BaseModel):
    dry_run: bool = Field(default=True, description="When true, performs full navigation and form detection without submitting")
    headless: bool = Field(default=True, description="Run headless browser session")
    custom_field_overrides: Optional[dict[str, str]] = None


class BrowserStatusResponse(BaseModel):
    application_id: str
    job_id: str
    company: str
    job_title: str
    application_url: str
    status: str
    current_step: str
    last_successful_step: Optional[str] = None
    form_detected: bool = False
    detected_fields: list[dict[str, Any]] = Field(default_factory=list)
    mapped_fields: dict[str, Any] = Field(default_factory=dict)
    fields_requiring_user_input: list[str] = Field(default_factory=list)
    captcha_detected: bool = False
    otp_detected: bool = False
    auth_required: bool = False
    cv_uploaded: bool = False
    cv_filename: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    confirmation_token: Optional[str] = None
    confirmation_message: Optional[str] = None
    confirmation_reference: Optional[str] = None
    submission_attempt_id: Optional[str] = None
    submitted_at: Optional[datetime] = None
    can_submit: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BrowserReviewResponse(BaseModel):
    application_id: str
    job_id: str
    company: str
    job_title: str
    application_url: str
    match_score: float
    recommendation: str
    cv_filename: str
    cv_path: Optional[str] = None
    cv_integrity: str
    cover_letter_preview: str
    fields: dict[str, Any]
    screening_questions: dict[str, Any]
    warnings: list[str]
    missing_fields: list[str]
    human_intervention_required: bool
    confirmation_token: str
    can_submit: bool
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ConfirmSubmitRequest(BaseModel):
    confirmation_token: str = Field(..., description="Mandatory single-use token generated by browser-review")
    reviewer_name: Optional[str] = "Candidate"
    notes: Optional[str] = None


class CancelSubmissionRequest(BaseModel):
    reason: Optional[str] = "Cancelled by user"


class SubmissionAuditLogResponse(BaseModel):
    id: str
    application_id: str
    job_id: str
    timestamp: datetime
    url: str
    browser_action: str
    fields_populated: dict[str, Any] = Field(default_factory=dict)
    files_uploaded: list[str] = Field(default_factory=list)
    human_approval: bool = False
    submission_result: str
    confirmation_result: Optional[str] = None
    errors: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


