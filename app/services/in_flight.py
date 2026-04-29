import asyncio
from typing import Any, Dict

in_flight: Dict[str, asyncio.Future] = {}
lock = asyncio.Lock()


async def get_or_create(key: str):
    async with lock:
        if key in in_flight:
            return in_flight[key]

        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        in_flight[key] = fut
        return fut


def resolve(key: str, value: Any):
    fut = in_flight.get(key)
    if fut and not fut.done():
        fut.set_result(value)
    in_flight.pop(key, None)


def fail(key: str, error: Exception):
    fut = in_flight.get(key)
    if fut and not fut.done():
        fut.set_exception(error)
    in_flight.pop(key, None)