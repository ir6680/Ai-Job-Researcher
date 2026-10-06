"""
Job Discovery Orchestration Service.
Coordinates:
1. Multi-source parallel job retrieval with timeouts
2. Cleaning & Normalization
3. Location validation (Lahore)
4. Entry-level validation
5. Deduplication against PostgreSQL database
6. Persistence & Audit metrics logging
"""

import asyncio
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from backend.app.config import settings
from backend.app.models import Job, JobDiscoveryRun
from backend.app.services.job_discovery.base_source import RawDiscoveredJob
from backend.app.services.job_discovery.job_cleaner_service import JobCleanerService
from backend.app.services.job_discovery.sources.registry import get_all_sources, get_source_by_id, resolve_source_ids
from backend.app.schemas import JobDiscoveryRunRequest
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class JobDiscoveryService:

    @classmethod
    async def run_discovery(
        cls,
        db: Session,
        request: Optional[JobDiscoveryRunRequest] = None
    ) -> JobDiscoveryRun:
        """
        Execute an end-to-end job discovery run across configured sources.
        Fault-tolerant: failures in individual sources are caught and logged.
        """
        # Resolve parameters
        req = request or JobDiscoveryRunRequest()
        keywords = req.keywords or settings.ENTRY_LEVEL_KEYWORDS
        source_keys = resolve_source_ids(req.sources or settings.JOB_SOURCES)
        target_city = req.target_city or settings.TARGET_CITY
        max_jobs = req.max_jobs_per_run or settings.MAX_JOBS_PER_RUN

        # Create discovery run record
        run = JobDiscoveryRun(
            triggered_at=datetime.utcnow(),
            status="running",
            sources_checked=source_keys,
            keywords_used=keywords,
            total_discovered=0,
            new_jobs_added=0,
            duplicates_skipped=0,
            rejected_non_lahore=0,
            rejected_non_entry=0
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        logger.info(f"[Run {run.id}] Starting job discovery for {target_city} across {len(source_keys)} sources...")

        # 1. Collect from all requested sources
        raw_jobs: List[RawDiscoveredJob] = []
        timeout_seconds = settings.DISCOVERY_REQUEST_TIMEOUT_SECONDS

        for key in source_keys:
            source = get_source_by_id(key)
            if not source or not source.is_active:
                logger.warning(f"Source '{key}' not found or inactive. Skipping.")
                continue

            try:
                # Wrap source invocation with timeout protection
                jobs_from_source = await asyncio.wait_for(
                    source.discover_jobs(keywords=keywords, target_city=target_city, limit=max_jobs),
                    timeout=timeout_seconds
                )
                logger.info(f"Source '{source.source_name}' returned {len(jobs_from_source)} jobs.")
                raw_jobs.extend(jobs_from_source)
            except asyncio.TimeoutError:
                logger.error(f"Source '{source.source_name}' timed out after {timeout_seconds}s. Proceeding.")
            except Exception as e:
                logger.error(f"Source '{source.source_name}' failed with error: {e}. Gracefully continuing.")

        run.total_discovered = len(raw_jobs)
        logger.info(f"[Run {run.id}] Raw jobs collected: {run.total_discovered}. Commencing cleaning & deduplication...")

        # 2. Process and filter jobs
        new_jobs_count = 0
        duplicates_count = 0
        non_lahore_count = 0
        non_entry_count = 0

        for raw_job in raw_jobs:
            # Step A: Clean and normalize
            cleaned_job = JobCleanerService.clean_and_normalize(raw_job)

            # Step B: Validate location (Lahore or Remote)
            is_lahore, loc_reason = JobCleanerService.is_lahore_location(
                cleaned_job.location, cleaned_job.description, target_city=target_city
            )
            if not is_lahore:
                non_lahore_count += 1
                logger.debug(f"Rejected non-Lahore job '{cleaned_job.job_title}' at {cleaned_job.company}: {loc_reason}")
                continue

            # Step C: Validate entry-level criteria
            is_entry, entry_reason = JobCleanerService.is_entry_level(
                cleaned_job.job_title,
                cleaned_job.description,
                cleaned_job.experience_requirement,
                keywords=keywords
            )
            if not is_entry:
                non_entry_count += 1
                logger.debug(f"Rejected non-entry job '{cleaned_job.job_title}' at {cleaned_job.company}: {entry_reason}")
                continue

            # Step D: Deduplication check
            is_dup, canonical_id = JobCleanerService.detect_duplicate(cleaned_job, db)
            if is_dup and not req.force_refresh:
                duplicates_count += 1
                logger.debug(f"Skipped duplicate job '{cleaned_job.job_title}' at {cleaned_job.company} (canonical: {canonical_id})")
                continue

            # Step E: Insert unique job into database
            dedup_hash = JobCleanerService.compute_dedup_hash(
                cleaned_job.company,
                cleaned_job.job_title,
                cleaned_job.location,
                cleaned_job.source_url,
                cleaned_job.description
            )

            job_record = Job(
                company=cleaned_job.company,
                job_title=cleaned_job.job_title,
                location=cleaned_job.location,
                job_url=cleaned_job.job_url or cleaned_job.source_url,
                source_url=cleaned_job.source_url,
                description=cleaned_job.description,
                raw_description=cleaned_job.raw_description,
                responsibilities=cleaned_job.responsibilities,
                required_skills=cleaned_job.required_skills,
                preferred_skills=cleaned_job.preferred_skills,
                experience_requirement=cleaned_job.experience_requirement,
                education_requirement=cleaned_job.education_requirement,
                job_type=cleaned_job.job_type,
                salary=cleaned_job.salary,
                source=cleaned_job.source,
                status="discovered",
                job_status="discovered",
                duplicate_status="unique",
                canonical_job_id=None,
                dedup_hash=dedup_hash,
                posting_date=cleaned_job.posting_date,
                deadline=cleaned_job.deadline,
                discovered_at=datetime.utcnow()
            )
            db.add(job_record)
            new_jobs_count += 1

            if new_jobs_count >= max_jobs:
                break

        # 3. Finalize run statistics
        run.completed_at = datetime.utcnow()
        run.status = "completed"
        run.new_jobs_added = new_jobs_count
        run.duplicates_skipped = duplicates_count
        run.rejected_non_lahore = non_lahore_count
        run.rejected_non_entry = non_entry_count

        db.commit()
        db.refresh(run)
        logger.info(
            f"[Run {run.id}] Completed successfully! Added: {new_jobs_count}, "
            f"Duplicates: {duplicates_count}, Non-Lahore: {non_lahore_count}, Non-Entry: {non_entry_count}."
        )
        return run

    @staticmethod
    def get_discovery_runs(db: Session, skip: int = 0, limit: int = 20) -> List[JobDiscoveryRun]:
        """Fetch past job discovery run audit records."""
        return db.query(JobDiscoveryRun).order_by(desc(JobDiscoveryRun.triggered_at)).offset(skip).limit(limit).all()

    @staticmethod
    def get_jobs(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        company: Optional[str] = None,
        source: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        duplicate_status: Optional[str] = "unique"
    ) -> List[Job]:
        """Query jobs with full faceted filtering."""
        query = db.query(Job)

        if duplicate_status:
            query = query.filter(Job.duplicate_status == duplicate_status)

        if search:
            query = query.filter(
                or_(
                    Job.job_title.ilike(f"%{search}%"),
                    Job.company.ilike(f"%{search}%"),
                    Job.description.ilike(f"%{search}%")
                )
            )

        if company:
            query = query.filter(Job.company.ilike(f"%{company}%"))

        if source:
            query = query.filter(Job.source.ilike(f"%{source}%"))

        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))

        if status:
            query = query.filter(
                or_(Job.status == status, Job.job_status == status)
            )

        return query.order_by(desc(Job.discovered_at)).offset(skip).limit(limit).all()

    @staticmethod
    def update_job_status(db: Session, job_id: str, new_status: str) -> Optional[Job]:
        """Update job status (discovered, saved, ignored, applied, archived)."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        job.status = new_status
        job.job_status = new_status
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def refresh_job(db: Session, job_id: str) -> Optional[Job]:
        """Re-clean and normalize an existing job record."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        raw = RawDiscoveredJob(
            company=job.company,
            job_title=job.job_title,
            location=job.location,
            description=job.description,
            raw_description=job.raw_description,
            responsibilities=job.responsibilities or [],
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
            experience_requirement=job.experience_requirement,
            education_requirement=job.education_requirement,
            job_type=job.job_type,
            salary=job.salary,
            source=job.source,
            source_url=job.source_url or job.job_url or "",
            job_url=job.job_url,
            posting_date=job.posting_date,
            deadline=job.deadline
        )
        cleaned = JobCleanerService.clean_and_normalize(raw)
        
        job.company = cleaned.company
        job.job_title = cleaned.job_title
        job.description = cleaned.description
        job.responsibilities = cleaned.responsibilities
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job
