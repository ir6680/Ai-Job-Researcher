"""
Browser Manager Component for Phase 6 Controlled Browser-Based Application Agent.
Manages Playwright lifecycle, context isolation, and security constraints.
"""

from typing import Optional, Tuple
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:
    """
    Manages Playwright browser instance, contexts, and pages.
    Guarantees controlled, isolated browser sessions with strict timeouts.
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self, headless: bool = True, timeout_ms: int = 30000):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def start_session(self) -> Tuple[BrowserContext, Page]:
        """Starts Playwright Chromium and initializes a fresh, isolated context."""
        try:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ]
            )
            self._context = self._browser.new_context(
                user_agent=self.DEFAULT_USER_AGENT,
                viewport={"width": 1280, "height": 800},
                accept_downloads=True,
                ignore_https_errors=False,
            )
            self._context.set_default_timeout(self.timeout_ms)
            self._context.set_default_navigation_timeout(self.timeout_ms)

            self._page = self._context.new_page()
            logger.info("Browser session started successfully in controlled mode.")
            return self._context, self._page
        except Exception as e:
            logger.error(f"Failed to start browser session: {e}")
            self.close()
            raise

    def get_page(self) -> Optional[Page]:
        return self._page

    def close(self):
        """Cleanly releases all browser resources."""
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
            logger.info("Browser session cleanly closed.")
        except Exception as e:
            logger.warning(f"Error during browser session shutdown: {e}")
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None

    def __enter__(self):
        self.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
