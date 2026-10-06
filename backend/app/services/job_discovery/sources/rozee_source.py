"""
Rozee.pk Job Board Source.
Connects to Rozee.pk Lahore IT listings, respecting anti-bot constraints.
"""

from typing import List
import httpx
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class RozeeJobSource(BaseJobSource):
    source_id = "rozee_pk"
    source_name = "Rozee.pk IT Board"
    source_type = "job_board"
    base_url = "https://www.rozee.pk/jobs-in-lahore"
    description = "Pakistan's job portal filtering for Lahore software & engineering jobs."

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live Rozee.pk portal...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                if resp.status_code == 403:
                    logger.warning(
                        f"[{self.source_id}] Rozee.pk returned HTTP 403 Forbidden. "
                        "Site enforces Cloudflare / Incapsula anti-bot challenge and restricts non-browser/cloud server traffic. "
                        "Respecting anti-bot policy and aborting gracefully without bypassing security controls."
                    )
                    return results

                logger.info(f"[{self.source_id}] Response status: {resp.status_code}")
        except Exception as e:
            logger.error(f"[{self.source_id}] Connection error or timeout: {e}")

        return results


class SearchEngineJobSource(BaseJobSource):
    source_id = "search_engine"
    source_name = "Lahore Tech Career Aggregator"
    source_type = "search_engine"
    base_url = "https://remotive.com/api/remote-jobs?category=software-dev"
    description = "Automated discovery from legitimate tech careers API open to Pakistan."

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live remote tech job feed...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient(headers=headers, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                if resp.status_code != 200:
                    logger.warning(f"[{self.source_id}] API returned HTTP {resp.status_code}")
                    return results

                data = resp.json()
                jobs = data.get("jobs", [])
                logger.info(f"[{self.source_id}] Found {len(jobs)} global tech opportunities.")

                for j in jobs:
                    loc = j.get("candidate_required_location", "")
                    title = j.get("title", "")
                    
                    # Accept Worldwide / Pakistan eligible
                    if not any(k in loc.lower() for k in ["worldwide", "anywhere", "pakistan"]):
                        continue

                    if keywords:
                        matches = any(
                            kw.lower() in title.lower() or any(term in title.lower() for term in ["engineer", "developer", "backend", "python", "software"])
                            for kw in keywords
                        )
                        if not matches:
                            continue

                    import re
                    clean_desc = re.sub(r'<[^>]+>', ' ', j.get("description", "")).strip()

                    results.append(
                        RawDiscoveredJob(
                            company=j.get("company_name", "Remote Tech"),
                            job_title=title,
                            location="Remote (Worldwide / Pakistan)",
                            description=clean_desc[:2500],
                            raw_description=clean_desc,
                            responsibilities=[],
                            required_skills=j.get("tags", [])[:6] or ["Software Engineering", "Python"],
                            preferred_skills=[],
                            experience_requirement="Entry-level to Junior",
                            education_requirement="BS Computer Science or equivalent experience",
                            job_type="Remote",
                            salary=j.get("salary") or "Competitive",
                            source="Global Tech Job Board",
                            source_url=j.get("url", ""),
                            job_url=j.get("url", ""),
                            posting_date=j.get("publication_date", "").split("T")[0] if j.get("publication_date") else None
                        )
                    )

                    if len(results) >= limit:
                        break

        except Exception as e:
            logger.error(f"[{self.source_id}] Live query failed: {e}")

        logger.info(f"[{self.source_id}] Extracted {len(results)} valid live jobs.")
        return results
