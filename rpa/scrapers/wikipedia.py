"""Playwright scraper that extracts the first paragraph of a Wikipedia article."""

from dataclasses import dataclass

import structlog
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

SEARCH_RESULT_TIMEOUT_MS = 5000
CONTENT_TIMEOUT_MS = 5000

log = structlog.get_logger(__name__)


@dataclass
class ScrapedArticle:
    """The extracted paragraph plus the article URL it was taken from."""

    paragraph: str
    source_url: str


class WikipediaScraper:
    """Extracts the first non-empty paragraph of a Wikipedia article."""

    BASE_URL = "https://es.wikipedia.org"

    def __init__(self, headless: bool = True) -> None:
        self._headless = headless

    async def extract_first_paragraph(self, term: str) -> ScrapedArticle:
        """Search `term` on Wikipedia and return its first paragraph and URL."""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self._headless)
            page = await browser.new_page()
            try:
                await page.goto(f"{self.BASE_URL}/wiki/Special:Search?search={term}")

                try:
                    await page.wait_for_selector(
                        ".mw-search-results a", timeout=SEARCH_RESULT_TIMEOUT_MS
                    )
                    await page.click(".mw-search-results a")
                except PlaywrightTimeoutError:
                    # Wikipedia redirected straight to the article; nothing to click.
                    log.info("scraper.direct_match", term=term, url=page.url)

                await page.wait_for_selector(
                    "#mw-content-text p", timeout=CONTENT_TIMEOUT_MS
                )
                paragraph = await page.locator(
                    "#mw-content-text p"
                ).first.inner_text(timeout=CONTENT_TIMEOUT_MS)
                source_url = page.url

                log.info(
                    "scraper.extracted", term=term, chars=len(paragraph), url=source_url
                )
                return ScrapedArticle(paragraph=paragraph.strip(), source_url=source_url)
            except Exception as exc:
                log.error("scraper.failed", term=term, error=str(exc))
                raise
            finally:
                await browser.close()
