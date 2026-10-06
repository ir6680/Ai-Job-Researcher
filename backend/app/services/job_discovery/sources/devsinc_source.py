"""
Devsinc Official Careers Source.
Connects directly to Devsinc's live Workable ATS widget & job details API.
"""

from typing import List
import httpx
from bs4 import BeautifulSoup
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class DevsincJobSource(BaseJobSource):
    source_id = "devsinc"
    source_name = "Devsinc Careers (Workable ATS)"
    source_type = "company_careers"
    base_url = "https://apply.workable.com/devsinc-17/"
    description = "Official Workable career portal of Devsinc (Lahore, Pakistan)."

    WIDGET_API_URL = "https://apply.workable.com/api/v1/widget/accounts/devsinc-17"
    JOB_DETAIL_API_URL = "https://apply.workable.com/api/v2/accounts/devsinc-17/jobs/{shortcode}"

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live Devsinc Workable ATS API...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient(headers=headers, timeout=12.0) as client:
                resp = await client.get(self.WIDGET_API_URL)
                if resp.status_code != 200:
                    logger.warning(f"[{self.source_id}] Workable returned HTTP {resp.status_code}")
                    return results

                data = resp.json()
                raw_openings = data.get("jobs", [])
                logger.info(f"[{self.source_id}] Total live openings found: {len(raw_openings)}")

                for item in raw_openings:
                    title = item.get("title", "").strip()
                    city = item.get("city", "")
                    country = item.get("country", "")
                    shortcode = item.get("shortcode", "")
                    job_url = item.get("url") or f"https://apply.workable.com/devsinc-17/j/{shortcode}/"

                    # Location check: Lahore / Pakistan
                    loc_str = f"{city}, {country}".strip(", ")
                    if target_city.lower() not in loc_str.lower() and "pakistan" not in loc_str.lower():
                        continue

                    # Keyword filter if supplied
                    if keywords:
                        matches = any(
                            kw.lower() in title.lower()
                            for kw in keywords
                        )
                        if not matches:
                            continue

                    # Fetch full description if shortcode available
                    description = f"Role: {title} at Devsinc in {loc_str}."
                    responsibilities: List[str] = []
                    req_skills: List[str] = []
                    pref_skills: List[str] = []

                    if shortcode:
                        try:
                            det_url = self.JOB_DETAIL_API_URL.format(shortcode=shortcode)
                            det_resp = await client.get(det_url)
                            if det_resp.status_code == 200:
                                det_data = det_resp.json()
                                raw_desc_html = det_data.get("description", "")
                                raw_req_html = det_data.get("requirements", "")
                                
                                desc_soup = BeautifulSoup(raw_desc_html, "html.parser")
                                req_soup = BeautifulSoup(raw_req_html, "html.parser")
                                
                                clean_desc = desc_soup.get_text(separator="\n", strip=True)
                                clean_req = req_soup.get_text(separator="\n", strip=True)
                                
                                if clean_desc or clean_req:
                                    description = f"{clean_desc}\n\nRequirements:\n{clean_req}".strip()

                                # Extract bullet requirements
                                for li in req_soup.find_all("li"):
                                    txt = li.get_text(strip=True)
                                    if len(txt) > 5:
                                        if any(k in txt.lower() for k in ["python", "sql", "git", "oop", "testing", "cloud", "api", "react", "fastapi"]):
                                            req_skills.append(txt[:80])
                                        else:
                                            responsibilities.append(txt[:100])
                        except Exception as e:
                            logger.debug(f"Failed to fetch detail for {shortcode}: {e}")

                    results.append(
                        RawDiscoveredJob(
                            company="Devsinc",
                            job_title=title,
                            location=loc_str or "Lahore, Pakistan",
                            description=description,
                            raw_description=description,
                            responsibilities=responsibilities[:8],
                            required_skills=req_skills[:8] or ["Python", "SQL", "Git", "OOP"],
                            preferred_skills=pref_skills,
                            experience_requirement="0-1 years (Entry-Level)" if any(k in title.lower() for k in ["associate", "trainee", "junior", "intern"]) else "1-3 years",
                            education_requirement="BS Computer Science / Software Engineering",
                            job_type="Full-time",
                            source="Devsinc Careers (Workable)",
                            source_url=job_url,
                            job_url=job_url,
                            posting_date=item.get("published_on", "").split("T")[0] if item.get("published_on") else None
                        )
                    )

                    if len(results) >= limit:
                        break

        except Exception as e:
            logger.error(f"[{self.source_id}] Live query failed: {e}")

        logger.info(f"[{self.source_id}] Extracted {len(results)} valid live jobs.")
        return results
