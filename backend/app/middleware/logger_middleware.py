import time
import uuid
from fastapi import Request, Response

import structlog

from app.utils.logger import get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next):
    """
    Production-grade HTTP logging middleware.

    Features:
    - request_id / trace_id propagation
    - structured logging via structlog
    - latency measurement
    - exception logging
    - context isolation per request
    """

    # Extract / generate correlation IDs
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4()),
    )

    trace_id = request.headers.get("X-Trace-ID")

    # Bind request context (VERY IMPORTANT)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        trace_id=trace_id,
        method=request.method,
        path=request.url.path,
    )

    # Timing start
    start_time = time.perf_counter()

    client_host = request.client.host if request.client else None

    # Log request start
    logger.info(
        "http_request_started",
        client_host=client_host,
        user_agent=request.headers.get("user-agent"),
        query_string=str(request.query_params) if request.query_params else None,
    )

    try:
        # Process request
        response: Response = await call_next(request)

        # Success metrics
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log success
        logger.info(
            "http_request_completed",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        # Attach request id to response
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception:
        # Error handling
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "http_request_failed",
            duration_ms=round(duration_ms, 2),
        )

        raise

    finally:
        # Cleanup
        structlog.contextvars.clear_contextvars()
