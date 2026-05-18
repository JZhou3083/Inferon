import asyncio
from typing import Any


# in-memory request coalescing registry
_in_flight: dict[str, asyncio.Future] = {}

# protects registry mutation
_lock = asyncio.Lock()


async def get_or_create(key: str,timeout: float = 30.0) -> asyncio.Future:
    """
    Returns existing in-flight future if present,
    otherwise creates and registers a new future.
    """

    async with _lock:

        existing = _in_flight.get(key)

        if existing:
            return existing

        loop = asyncio.get_running_loop()

        future = loop.create_future()

        _in_flight[key] = future

        async def _cleanup():
            try:
                await asyncio.sleep(timeout)
                if not future.done():
                    fail(key, TimeoutError(f"In-flight request timeout after {timeout}s"))
            except asyncio.CancelledError:
                pass
        
        asyncio.create_task(_cleanup())

        return future


def resolve(key: str, value: Any):
    """
    Resolves and removes in-flight future.
    """

    future = _in_flight.get(key)

    if future and not future.done():
        future.set_result(value)

    _in_flight.pop(key, None)


def fail(key: str, error: Exception):
    """
    Fails and removes in-flight future.
    """

    future = _in_flight.get(key)

    if future and not future.done():
        future.set_exception(error)

    _in_flight.pop(key, None)