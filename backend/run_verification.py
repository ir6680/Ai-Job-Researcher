"""
Real End-to-End Phase 2 Job Discovery Verification Runner.
Executes live job collection using:
- TARGET_CITY=Lahore
- TARGET_COUNTRY=Pakistan
- MAX_JOBS_PER_RUN=20
"""

import asyncio
import os
import sys
from datetime import datetime

# Set PYTHONPATH
sys.path.insert(0, "/app/applet")

from backend.app.config import settings
from backend.app.database import init_db, SessionLocal
from backend.app.models import Job, JobDiscoveryRun
from backend.app.schemas import JobDiscoveryRunRequest
from backend.app.services.job_discovery.discovery_service import JobDiscoveryService
from backend.app.services.job_discovery.sources.registry import get_all_sources


async def run_verification():
    print("=" * 70)
    print("PHASE 2 REAL END-TO-END VERIFICATION RUN")
    print("=" * 70)
    print(f"Target City: {settings.TARGET_CITY}")
    print(f"Target Country: {settings.TARGET_COUNTRY}")
    print(f"Max Jobs Per Run: 20")
    print(f"Configured Sources: {settings.JOB_SOURCES}")
    print("=" * 70)

    # 1. Initialize database schema
    init_db()
    db = SessionLocal()

    try:
        # Create request object
        req = JobDiscoveryRunRequest(
            target_city="Lahore",
            keywords=[
                "Python Developer",
                "Backend Developer",
                "Software Engineer",
                "Junior Developer",
                "AI/ML Engineer",
                "QA Engineer",
                "QA Automation Engineer",
                "Software Intern",
                "Trainee Engineer",
                "Associate Software Engineer",
                "Full Stack Developer"
            ],
            sources=settings.JOB_SOURCES,
            max_jobs_per_run=20,
            force_refresh=False
        )

        print("\n[Step 1] Triggering live JobDiscoveryService.run_discovery()...\n")
        start_time = datetime.utcnow()
        run_record = await JobDiscoveryService.run_discovery(db=db, request=req)
        end_time = datetime.utcnow()

        duration = (end_time - start_time).total_seconds()
        print(f"\n[Step 2] Discovery run completed in {duration:.2f} seconds.")
        print(f"Run ID: {run_record.id}")
        print(f"Status: {run_record.status}")

        # Fetch newly stored jobs from DB
        stored_jobs = db.query(Job).filter(Job.discovered_at >= start_time).all()
        all_stored_jobs = db.query(Job).all()

        print("\n" + "=" * 70)
        print("SUMMARY METRICS")
        print("=" * 70)
        print(f"1. Total Jobs Discovered from Live Sources: {run_record.total_discovered}")
        print(f"2. Jobs Accepted (Passed Lahore + Entry-level filters): {run_record.new_jobs_added}")
        print(f"3. Jobs Rejected:")
        print(f"   - Non-Lahore Location: {run_record.rejected_non_lahore}")
        print(f"   - Non-Entry-Level / Senior Role: {run_record.rejected_non_entry}")
        print(f"   - Total Rejected: {run_record.rejected_non_lahore + run_record.rejected_non_entry}")
        print(f"4. Duplicates Detected & Skipped: {run_record.duplicates_skipped}")
        print(f"5. Total Jobs Persisted in Database: {len(stored_jobs)} (Total in DB: {len(all_stored_jobs)})")

        print("\n" + "=" * 70)
        print("SOURCE STATUS AUDIT")
        print("=" * 70)
        all_sources = get_all_sources()
        for sid, src in all_sources.items():
            print(f"- {src.source_name} ({sid}):")
            print(f"  Base URL: {src.base_url}")
            print(f"  Type: {src.source_type}")

        print("\n" + "=" * 70)
        print("REAL COLLECTED JOBS EXAMPLES (STORED IN DATABASE)")
        print("=" * 70)

        for i, j in enumerate(stored_jobs[:5], 1):
            print(f"\n--- Job #{i} ---")
            print(f"Company: {j.company}")
            print(f"Job Title: {j.job_title}")
            print(f"Location: {j.location}")
            print(f"Source: {j.source}")
            print(f"Source URL: {j.source_url}")
            print(f"Experience Requirement: {j.experience_requirement}")
            print(f"Education Requirement: {j.education_requirement}")
            print(f"Required Skills: {j.required_skills}")
            print(f"Responsibilities Sample: {j.responsibilities[:3] if j.responsibilities else 'None listed'}")
            print(f"Posting Date: {j.posting_date}")
            print(f"Dedup Hash: {j.dedup_hash}")
            print(f"Description (First 250 chars):\n{j.description[:250]}...")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_verification())
