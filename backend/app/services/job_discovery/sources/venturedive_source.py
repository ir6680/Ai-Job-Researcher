"""
VentureDive Official Careers Source.
Live web scraping for official VentureDive JazzHR career portal (Lahore DHA Phase 5).
"""

from typing import List
import httpx
from bs4 import BeautifulSoup
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class VentureDiveJobSource(BaseJobSource):
    source_id = "venturedive"
    source_name = "VentureDive Careers (JazzHR)"
    source_type = "company_careers"
    base_url = "https://venturedive.applytojob.com/apply/"
    description = "Official JazzHR career portal of VentureDive (Lahore DHA Phase 5)."

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live VentureDive JazzHR portal...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                if resp.status_code != 200:
                    logger.warning(f"[{self.source_id}] JazzHR portal returned HTTP {resp.status_code}")
                    return results

                soup = BeautifulSoup(resp.text, "html.parser")
                openings = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/apply/" in href and href != "/apply/" and "#" not in href:
                        t = a.get_text(strip=True)
                        if t and len(t) > 4:
                            openings.append((t, href))

                logger.info(f"[{self.source_id}] Found {len(openings)} live openings.")

                for title, job_url in openings:
                    if keywords:
                        matches = any(
                            kw.lower() in title.lower() or any(term in title.lower() for term in ["engineer", "developer", "support", "analyst", "qa", "associate"])
                            for kw in keywords
                        )
                        if not matches:
                            continue

                    description = f"{title} at VentureDive (Lahore office)."
                    responsibilities: List[str] = []
                    req_skills: List[str] = []

                    job_loc = "Lahore, Pakistan"
                    try:
                        det_resp = await client.get(job_url)
                        if det_resp.status_code == 200:
                            det_soup = BeautifulSoup(det_resp.text, "html.parser")
                            paras = [p.get_text(strip=True) for p in det_soup.find_all("p") if len(p.get_text(strip=True)) > 30 and "resume" not in p.get_text(strip=True).lower()]
                            if paras:
                                description = "\n\n".join(paras[:6])
                                if "karachi" in description[:300].lower():
                                    job_loc = "Karachi, Pakistan"
                                elif "islamabad" in description[:300].lower():
                                    job_loc = "Islamabad, Pakistan"

                            lis = [li.get_text(strip=True) for li in det_soup.find_all("li") if len(li.get_text(strip=True)) > 15]
                            for item in lis:
                                if any(k in item.lower() for k in ["experience", "degree", "skills", "knowledge", "bachelor"]):
                                    req_skills.append(item[:80])
                                else:
                                    responsibilities.append(item[:100])
                    except Exception as e:
                        logger.debug(f"Failed to fetch detail for {job_url}: {e}")

                    results.append(
                        RawDiscoveredJob(
                            company="VentureDive",
                            job_title=title,
                            location=job_loc,
                            description=description,
                            raw_description=description,
                            responsibilities=responsibilities[:8],
                            required_skills=req_skills[:8] or ["Problem Solving", "Software Engineering", "Git"],
                            preferred_skills=["Python", "Cloud", "Linux"],
                            experience_requirement="0-2 years",
                            education_requirement="BS Computer Science / Software Engineering / IT",
                            job_type="Full-time",
                            source="VentureDive Careers",
                            source_url=job_url,
                            job_url=job_url
                        )
                    )

                    if len(results) >= limit:
                        break

        except Exception as e:
            logger.error(f"[{self.source_id}] Live query failed: {e}")

        logger.info(f"[{self.source_id}] Extracted {len(results)} valid live jobs.")
        return results
