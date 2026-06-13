from __future__ import annotations

import logging
import sys
from typing import Optional

import structlog


def configure_logging(
    *,
    level: str = "INFO",
    environment: str = "production",
) -> None:
    """
    Configure structured logging.

    Args:
        level:
            DEBUG | INFO | WARNING | ERROR | CRITICAL

        environment:
            development | staging | production
    """

    shared_processors = [
        structlog.contextvars.merge_contextvars,  # adds each value from contextvar to each log
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=True,
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if environment.lower() == "production":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    # avoid duplicate handlers
    root_logger.handlers.clear()

    root_logger.addHandler(handler)
    root_logger.setLevel(level.upper())

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def bind_request_context(
    *,
    request_id: str,
    user_id: str | None = None,
    trace_id: str | None = None,
) -> None:
    context = {
        "request_id": request_id,
    }
    if user_id:
        context["user_id"] = user_id
    if trace_id:
        context["trace_id"] = trace_id

    structlog.contextvars.bind_contextvars(**context)


def get_logger(name: Optional[str] = None):
    return structlog.get_logger(name)
