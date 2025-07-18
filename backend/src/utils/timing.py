import time
import functools
import logging

logger = logging.getLogger(__name__)

def log_execution_time(label: str = ""):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            end = time.perf_counter()
            logger.info(f"{label or func.__name__} took {end - start:.3f} seconds")
            return result
        return wrapper
    return decorator
