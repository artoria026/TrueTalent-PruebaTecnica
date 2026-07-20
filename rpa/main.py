"""Entrypoint: scrapes a Wikipedia paragraph, saves it, then summarizes it."""

import asyncio
import sys

import httpx
import structlog

from rpa.config import RpaSettings
from rpa.logging_config import configure_logging
from rpa.scrapers.wikipedia import ScrapedArticle, WikipediaScraper

log = structlog.get_logger(__name__)


async def _save_extraction(
    settings: RpaSettings, term: str, article: ScrapedArticle
) -> bool:
    """Record the scraped paragraph and its source. Returns whether it succeeded."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.rpa_results_api_url,
                json={
                    "term": term,
                    "paragraph": article.paragraph,
                    "source_url": article.source_url,
                },
            )
            response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.error("rpa.save_extraction_failed", error=str(exc))
        return False


async def _summarize(settings: RpaSettings, paragraph: str) -> str | None:
    """Send the scraped text to the assistant API. Returns None on failure."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.assistant_api_url,
                json={
                    "user_id": settings.assistant_user_id,
                    "text": paragraph,
                    # Opt out of the mock fallback: better no summary than a fake one.
                    "allow_fallback": False,
                },
            )
            response.raise_for_status()
            return response.json()["summary"]
    except httpx.HTTPStatusError as exc:
        error = exc.response.json().get("error", {}) if exc.response.content else {}
        if error.get("code") == "AI_QUOTA_EXCEEDED":
            log.error(
                "rpa.summarize_quota_exceeded",
                message=error.get("message"),
                retry_after_seconds=error.get("retry_after_seconds"),
            )
        else:
            log.error(
                "rpa.summarize_failed",
                status_code=exc.response.status_code,
                message=error.get("message") or str(exc),
            )
        return None
    except httpx.HTTPError as exc:
        log.error("rpa.summarize_failed", error=str(exc))
        return None


async def main() -> None:
    """Scrape a Wikipedia paragraph, record it, and summarize it via AI."""
    settings = RpaSettings()
    configure_logging(settings)

    term = sys.argv[1] if len(sys.argv) > 1 else settings.default_search_term
    log.info("rpa.started", term=term, headless=settings.headless)

    scraper = WikipediaScraper(headless=settings.headless)
    article = await scraper.extract_first_paragraph(term)
    log.info(
        "rpa.scraped", term=term, chars=len(article.paragraph), url=article.source_url
    )

    saved = await _save_extraction(settings, term, article)
    if not saved:
        # Nothing was persisted at all — this is the one case worth a hard exit.
        sys.exit(1)

    log.info(
        "rpa.extraction_saved",
        term=term,
        paragraph=article.paragraph,
        source_url=article.source_url,
    )

    summary = await _summarize(settings, article.paragraph)
    if summary is None:
        log.warning(
            "rpa.finished_without_summary",
            term=term,
            note="La extracción sí quedó guardada; solo falló el resumen de IA.",
        )
        sys.exit(1)

    log.info("rpa.finished", term=term, summary=summary)


if __name__ == "__main__":
    asyncio.run(main())
