"""
Systems Limited Official Careers Source.
Connects to Systems Limited's careers site and SAP SuccessFactors enterprise portal.
"""

from typing import List
import httpx
from bs4 import BeautifulSoup
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class SystemsLimitedJobSource(BaseJobSource):
    source_id = "systems_limited"
    source_name = "Systems Limited Careers"
    source_type = "company_careers"
    base_url = "https://www.systemsltd.com/careers"
    description = "Official career portal of Systems Limited (Pakistan's largest IT exporter)."

    SAP_CAREERS_URL = "https://career55.sapsf.eu/career?company=systemvent&career_ns=job_listing_summary&navBarLevel=JOB_SEARCH"

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live Systems Limited portal...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                # 1. Probe primary website careers page
                resp = await client.get(self.base_url)
                logger.info(f"[{self.source_id}] Career page response: HTTP {resp.status_code} ({len(resp.text)} bytes)")

                # 2. Probe SAP SuccessFactors
                sap_resp = await client.get(self.SAP_CAREERS_URL)
                logger.info(f"[{self.source_id}] SAP SuccessFactors response: HTTP {sap_resp.status_code} ({len(sap_resp.text)} bytes)")

                # Note: SAP SuccessFactors uses dynamic client-side JS rendering and stateful CSRF sessions (_s.crb token)
                # Static HTML scraping cannot evaluate JavaScript bundles without headless browser (Playwright is out of scope for Phase 2).
                soup = BeautifulSoup(sap_resp.text, "html.parser")
                jobs_found = soup.find_all("a", href=lambda h: h and "career_job_req_id" in h)
                if not jobs_found:
                    logger.warning(
                        f"[{self.source_id}] SAP SuccessFactors table requires dynamic client-side JavaScript execution (XHR session handshake). "
                        "No static job rows accessible via raw HTTP GET."
                    )

        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to query Systems Limited live endpoints: {e}")

        return results
