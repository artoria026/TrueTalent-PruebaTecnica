"""structlog configuration for the RPA module."""

import logging
import sys

import structlog

from rpa.config import RpaSettings


def configure_logging(settings: RpaSettings) -> None:
    """Configure structlog for the RPA scripts."""
    logging.basicConfig(stream=sys.stdout, level=settings.log_level)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
