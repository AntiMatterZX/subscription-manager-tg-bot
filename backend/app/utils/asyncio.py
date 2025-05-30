import asyncio
from typing import Any, Callable, Coroutine


def async_to_sync(async_func: Callable[..., Coroutine[Any, Any, Any]]):
    """Decorator to convert async function to sync"""

    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(async_func(*args, **kwargs))
        else:
            # Event loop is running, use nest_asyncio or thread
            try:
                import nest_asyncio

                nest_asyncio.apply()
                return asyncio.run(async_func(*args, **kwargs))
            except ImportError:
                # Use thread-based approach
                import concurrent.futures

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    try:
                        return new_loop.run_until_complete(async_func(*args, **kwargs))
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()

    return wrapper
