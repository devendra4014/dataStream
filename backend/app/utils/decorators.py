import asyncio
from functools import wraps
from inspect import iscoroutinefunction
import time
from .logger import get_logger

logger = get_logger(__name__)


def with_retry(max_retry=3, backoff=0.2):
    """A decorator for retry mechanism."""

    def decorator(func):
        def _retry_call(callable_func, *args, **kwargs):
            last_exception = None
            for attempt in range(max_retry):
                try:
                    return callable_func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retry - 1:
                        logger.error(f"Max retries are exceeded: {str(e)}")
                        raise
                    wait_time = backoff * (attempt + 1)
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {wait_time} sec"
                    )
                    time.sleep(wait_time)
            raise last_exception

        async def _retry_call_async(callable_func, *args, **kwargs):
            last_exception = None
            for attempt in range(max_retry):
                try:
                    return await callable_func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retry - 1:
                        logger.error(f"Max retries are exceeded: {str(e)}")
                        raise
                    wait_time = backoff * (attempt + 1)
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {wait_time} sec"
                    )
                    await asyncio.sleep(wait_time)
            raise last_exception

        if iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await _retry_call_async(func, *args, **kwargs)

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                return _retry_call(func, *args, **kwargs)

        return wrapper

    return decorator
