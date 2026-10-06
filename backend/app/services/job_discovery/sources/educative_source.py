"""
Educative Official Careers Source.
Connects directly to Educative's live Lever ATS API.
"""

from typing import List
import httpx
from bs4 import BeautifulSoup
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class EducativeJobSource(BaseJobSource):
    source_id = "educative"
    source_name = "Educative.io Careers (Lever ATS)"
    source_type = "company_careers"
    base_url = "https://jobs.lever.co/educative"
    description = "Official Lever ATS career portal of Educative (Lahore Engineering Office)."

    LEVER_API_URL = "https://api.lever.co/v0/postings/educative?mode=json"

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live Educative Lever ATS API...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient(headers=headers, timeout=12.0) as client:
                resp = await client.get(self.LEVER_API_URL)
                if resp.status_code != 200:
                    logger.warning(f"[{self.source_id}] Lever API returned HTTP {resp.status_code}")
                    return results

                postings = resp.json()
                logger.info(f"[{self.source_id}] Total live openings found: {len(postings)}")

                for p in postings:
                    title = p.get("text", "").strip()
                    categories = p.get("categories", {})
                    location = categories.get("location", "")
                    hosted_url = p.get("hostedUrl", "")

                    # Check location for Lahore or Pakistan
                    if target_city.lower() not in location.lower() and "pakistan" not in location.lower():
                        continue

                    # Keyword filter if supplied
                    if keywords:
                        matches = any(
                            kw.lower() in title.lower() or kw.lower() in str(categories).lower()
                            for kw in keywords
                        )
                        if not matches:
                            continue

                    # Extract plain text description and lists
                    desc_plain = p.get("descriptionPlain", "").strip()
                    lists = p.get("lists", [])
                    
                    responsibilities: List[str] = []
                    req_skills: List[str] = []

                    full_desc_parts = [desc_plain]

                    for lst in lists:
                        header = lst.get("text", "")
                        content = lst.get("content", "")
                        soup = BeautifulSoup(content, "html.parser")
                        items = [li.get_text(strip=True) for li in soup.find_all("li")]
                        if items:
                            full_desc_parts.append(f"\n{header}:\n" + "\n".join(f"- {it}" for it in items))
                            if "about you" in header.lower() or "requirement" in header.lower() or "qualif" in header.lower():
                                req_skills.extend(items)
                            else:
                                responsibilities.extend(items)

                    full_description = "\n\n".join(p for p in full_desc_parts if p).strip()
                    if not full_description:
                        full_description = f"{title} at Educative in {location}."

                    results.append(
                        RawDiscoveredJob(
                            company="Educative",
                            job_title=title,
                            location=f"{location}, Pakistan" if "pakistan" not in location.lower() else location,
                            description=full_description,
                            raw_description=full_description,
                            responsibilities=responsibilities[:8],
                            required_skills=req_skills[:8] or ["Computer Science", "Algorithms", "Data Structures", "Python/Java"],
                            preferred_skills=["Docker", "Cloud", "Distributed Systems"],
                            experience_requirement="Entry-level (0-1 years)" if any(k in title.lower() for k in ["entry", "junior", "associate", "intern"]) else "1-3 years",
                            education_requirement="BS / MS in Computer Science or related field",
                            job_type="Full-time",
                            source="Educative Careers (Lever)",
                            source_url=hosted_url,
                            job_url=hosted_url
                        )
                    )

                    if len(results) >= limit:
                        break

        except Exception as e:
            logger.error(f"[{self.source_id}] Live query failed: {e}")

        logger.info(f"[{self.source_id}] Extracted {len(results)} valid live jobs.")
        return results
