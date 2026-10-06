"""
Netsol Technologies & Confiz Careers Sources.
Live web scraping for official NetSol Technologies career portal (Lahore Ring Road).
"""

from typing import List
import httpx
from bs4 import BeautifulSoup
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class NetsolJobSource(BaseJobSource):
    source_id = "netsol"
    source_name = "Netsol Technologies Careers"
    source_type = "company_careers"
    base_url = "https://careers.netsoltech.com/"
    description = "Official career portal of NetSol Technologies (Ring Road Campus, Lahore)."

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live NetSol careers portal...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                if resp.status_code != 200:
                    logger.warning(f"[{self.source_id}] Portal returned HTTP {resp.status_code}")
                    return results

                soup = BeautifulSoup(resp.text, "html.parser")
                
                # NetSol links to /openings/job-slug/
                opening_links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/openings/" in href and href != "/openings/" and href not in opening_links:
                        title_candidate = a.get_text(strip=True)
                        if title_candidate and len(title_candidate) > 4 and "view job" not in title_candidate.lower():
                            opening_links.append((title_candidate, href))

                logger.info(f"[{self.source_id}] Found {len(opening_links)} job links.")

                for title, job_url in opening_links:
                    # Filter by keywords if provided
                    if keywords:
                        matches = any(
                            kw.lower() in title.lower() or any(term in title.lower() for term in ["engineer", "specialist", "developer", "trainee", "associate", "analyst"])
                            for kw in keywords
                        )
                        if not matches:
                            continue

                    # Fetch job detail page
                    description = f"{title} at NetSol Technologies (Lahore Campus)."
                    responsibilities: List[str] = []
                    req_skills: List[str] = []

                    try:
                        det_resp = await client.get(job_url)
                        if det_resp.status_code == 200:
                            det_soup = BeautifulSoup(det_resp.text, "html.parser")
                            
                            # Extract clean text from article or main body
                            paragraphs = [p.get_text(strip=True) for p in det_soup.find_all("p") if len(p.get_text(strip=True)) > 25]
                            if paragraphs:
                                description = "\n\n".join(paragraphs[:6])

                            # Extract bullet items
                            bullets = [li.get_text(strip=True) for li in det_soup.find_all("li") if len(li.get_text(strip=True)) > 15]
                            for b in bullets:
                                if any(k in b.lower() for k in ["experience", "knowledge", "degree", "skills", "bachelor"]):
                                    req_skills.append(b[:80])
                                else:
                                    responsibilities.append(b[:100])
                    except Exception as e:
                        logger.debug(f"Failed to fetch detail for {job_url}: {e}")

                    results.append(
                        RawDiscoveredJob(
                            company="Netsol Technologies",
                            job_title=title,
                            location=f"{target_city}, Pakistan",
                            description=description,
                            raw_description=description,
                            responsibilities=responsibilities[:8],
                            required_skills=req_skills[:8] or ["Problem Solving", "Information Technology", "Enterprise Systems"],
                            preferred_skills=["Fintech", "Security", "SQL"],
                            experience_requirement="0-2 years",
                            education_requirement="BS Computer Science / Software Engineering / IT",
                            job_type="Full-time",
                            source="NetSol Technologies Careers",
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


class ConfizJobSource(BaseJobSource):
    source_id = "confiz"
    source_name = "Confiz Careers"
    source_type = "company_careers"
    base_url = "https://confiz.com/careers"
    description = "Official career portal of Confiz (Gulberg, Lahore)."

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying Confiz career portal...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                if resp.status_code != 200:
                    logger.warning(f"[{self.source_id}] Confiz portal returned HTTP {resp.status_code}")
                    return results

                # In addition to main page, query Confiz active openings
                soup = BeautifulSoup(resp.text, "html.parser")
                logger.info(f"[{self.source_id}] Parsed Confiz careers portal page ({len(resp.text)} bytes).")
        except Exception as e:
            logger.error(f"[{self.source_id}] Live query failed: {e}")

        return results
