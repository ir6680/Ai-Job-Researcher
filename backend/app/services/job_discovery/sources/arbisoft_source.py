"""
Arbisoft Official Careers Source.
Connects to Arbisoft's careers portal and HireStream ATS.
"""

from typing import List
import httpx
from bs4 import BeautifulSoup
from backend.app.services.job_discovery.base_source import BaseJobSource, RawDiscoveredJob
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class ArbisoftJobSource(BaseJobSource):
    source_id = "arbisoft"
    source_name = "Arbisoft Careers"
    source_type = "company_careers"
    base_url = "https://arbisoft.com/careers"
    description = "Official career portal of Arbisoft Lahore (Canal Road, Thokar Campus)."

    HIRESTREAM_URL = "https://arbisoft.hirestream.io/careers/"

    async def discover_jobs(
        self,
        keywords: List[str],
        target_city: str = "Lahore",
        limit: int = 20
    ) -> List[RawDiscoveredJob]:
        logger.info(f"[{self.source_id}] Querying live Arbisoft portal...")
        results: List[RawDiscoveredJob] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(self.base_url)
                logger.info(f"[{self.source_id}] Career page response: HTTP {resp.status_code} ({len(resp.text)} bytes)")

                # Probe HireStream
                hs_resp = await client.get(self.HIRESTREAM_URL)
                logger.info(f"[{self.source_id}] HireStream ATS response: HTTP {hs_resp.status_code} ({len(hs_resp.text)} bytes)")

                # Test internal HireStream API
                api_resp = await client.get("https://app.hirestream.io/api/v1/jobs/")
                if api_resp.status_code == 401:
                    logger.warning(
                        f"[{self.source_id}] Arbisoft HireStream API returned HTTP 401 Unauthorized. "
                        "HireStream requires authenticated portal bearer token / client-side session."
                    )

        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to query Arbisoft live endpoints: {e}")

        return results
