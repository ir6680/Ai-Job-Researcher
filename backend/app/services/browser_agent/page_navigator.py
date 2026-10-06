"""
Page Navigator Component for Phase 6 Controlled Browser-Based Application Agent.
Handles URL validation, domain security, redirection protection, and page reachability.
"""

from urllib.parse import urlparse
from typing import Dict, Any, Optional
from playwright.sync_api import Page, Response
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class NavigationResult:
    def __init__(
        self,
        success: bool,
        current_url: str,
        status_code: Optional[int] = None,
        title: str = "",
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        redirected_unrelated_domain: bool = False,
    ):
        self.success = success
        self.current_url = current_url
        self.status_code = status_code
        self.title = title
        self.error_code = error_code
        self.error_message = error_message
        self.redirected_unrelated_domain = redirected_unrelated_domain


class PageNavigator:
    """
    Safely navigates to job application pages with strict domain boundary enforcement.
    Blocks redirects to suspicious or unrelated apex domains.
    """

    @staticmethod
    def extract_apex_domain(url: str) -> str:
        """Extracts the registered domain or host from a URL."""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower().split(":")[0]
        # Remove common prefixes like 'www.' or 'careers.'
        parts = netloc.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return netloc

    @classmethod
    def is_domain_allowed(cls, target_url: str, current_url: str) -> bool:
        """
        Verifies that current_url is within the same domain hierarchy or known ATS subdomains.
        Prevents submitting data to unrelated redirect targets.
        """
        target_apex = cls.extract_apex_domain(target_url)
        current_apex = cls.extract_apex_domain(current_url)

        # Allow same apex domain
        if target_apex == current_apex:
            return True

        # Known legitimate ATS platforms that software houses commonly redirect to
        legitimate_ats_domains = {
            "greenhouse.io", "lever.co", "workable.com", "bamboohr.com",
            "recruitee.com", "ashbyhq.com", "smartrecruiters.com",
            "jobvite.com", "rozee.pk", "linkedin.com"
        }
        if current_apex in legitimate_ats_domains:
            logger.info(f"Target redirected to recognized ATS domain: {current_apex}")
            return True

        return False

    @classmethod
    def navigate_to_application_url(
        cls,
        page: Page,
        target_url: str,
        expected_company: Optional[str] = None,
        timeout_ms: int = 25000
    ) -> NavigationResult:
        """
        Navigates to the application URL and performs security checks.
        """
        if not target_url or not target_url.startswith(("http://", "https://")):
            return NavigationResult(
                success=False,
                current_url="",
                error_code="INVALID_URL_SCHEME",
                error_message=f"Application URL '{target_url}' is not a valid HTTP/HTTPS address."
            )

        logger.info(f"Navigating to application URL: {target_url}")
        response: Optional[Response] = None

        try:
            response = page.goto(target_url, wait_until="domcontentloaded", timeout=timeout_ms)
        except Exception as e:
            err_str = str(e)
            logger.error(f"Navigation failed for {target_url}: {err_str}")
            return NavigationResult(
                success=False,
                current_url=page.url or target_url,
                error_code="PAGE_UNREACHABLE",
                error_message=f"Unable to reach destination URL: {err_str}"
            )

        current_url = page.url
        status_code = response.status if response else None

        # Check HTTP status
        if status_code and status_code >= 400:
            return NavigationResult(
                success=False,
                current_url=current_url,
                status_code=status_code,
                error_code="HTTP_ERROR",
                error_message=f"Destination returned HTTP status {status_code}."
            )

        # Check domain redirect safety
        if not cls.is_domain_allowed(target_url, current_url):
            logger.warning(
                f"Suspicious or unrelated domain redirection detected: {target_url} -> {current_url}"
            )
            return NavigationResult(
                success=False,
                current_url=current_url,
                status_code=status_code,
                redirected_unrelated_domain=True,
                error_code="UNRELATED_DOMAIN_REDIRECT",
                error_message=(
                    f"Navigation redirected to an unrelated domain '{current_url}'. "
                    "Submission blocked to prevent data exfiltration."
                )
            )

        page_title = page.title()
        logger.info(f"Page loaded: '{page_title}' at {current_url}")

        return NavigationResult(
            success=True,
            current_url=current_url,
            status_code=status_code,
            title=page_title
        )
