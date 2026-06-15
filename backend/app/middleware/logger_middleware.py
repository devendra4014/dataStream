import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

from app.utils.logger import get_logger

logger = get_logger(__name__)


async def logging_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        trace_id=trace_id,
        method=request.method,
        path=request.url.path,
    )

    start_time = time.perf_counter()

    client_host = (
        request.headers.get("X-Forwarded-For")
        or request.headers.get("X-Real-IP")
        or (request.client.host if request.client else None)
    )

    logger.info(
        "http_request_started",
        client_host=client_host,
        user_agent=request.headers.get("user-agent"),
        query_string=str(request.query_params) if request.query_params else None,
    )

    try:
        response: Response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "http_request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
            success=200 <= response.status_code < 400,
        )

        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.exception(
            "http_request_failed",
            duration_ms=duration_ms,
            error_type=type(exc).__name__,
        )
        raise

    finally:
        structlog.contextvars.clear_contextvars()
