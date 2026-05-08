import asyncio
import time
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)

from cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
)

from orchestration.in_flight import (
    get_or_create,
    resolve,
    fail,
)

from observability.logging import logger

from schemas.internal.chat import LLMResult


# ----------------------------------------
# concurrency protection
# ----------------------------------------

SEMAPHORE = asyncio.Semaphore(5)


# ----------------------------------------
# retry wrapper
# ----------------------------------------

@retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(min=1, max=8),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
async def _execute_with_retry(
    provider,
    prompt: str,
    timeout: int,
):
    async with SEMAPHORE:
        return await provider.complete(
            prompt=prompt,
            timeout=timeout,
        )


# ----------------------------------------
# public executor API
# ----------------------------------------

async def execute(
    *,
    provider,
    prompt: str,
    trace_id: str,
    timeout: int = 20,
) -> LLMResult:

    cache_key = build_cache_key(prompt)

    # ----------------------------------------
    # 1. cache lookup
    # ----------------------------------------

    cached = get_cache(cache_key)

    if cached:
        logger.info({
            "trace_id": trace_id,
            "event": "cache_hit",
        })

        return LLMResult(
            text=cached,
            cache_hit=True,
        )

    logger.info({
        "trace_id": trace_id,
        "event": "cache_miss",
    })

    # ----------------------------------------
    # 2. in-flight deduplication
    # ----------------------------------------

    future = await get_or_create(cache_key)

    # another coroutine already completed it
    if future.done():
        return LLMResult(
            text=future.result(),
            cache_hit=False,
        )

    # ----------------------------------------
    # 3. provider execution
    # ----------------------------------------

    started = time.time()

    try:

        output = await _execute_with_retry(
            provider=provider,
            prompt=prompt,
            timeout=timeout,
        )

        # ----------------------------------------
        # 4. cache write
        # ----------------------------------------

        set_cache(cache_key, output)

        # ----------------------------------------
        # 5. resolve shared future
        # ----------------------------------------

        resolve(
            cache_key,
            output,
        )

        logger.info({
            "trace_id": trace_id,
            "event": "llm_success",
            "latency": time.time() - started,
            "response_len": len(output),
        })

        return LLMResult(
            text=output,
            cache_hit=False,
        )

    except Exception as e:

        fail(
            cache_key,
            e,
        )

        logger.warning({
            "trace_id": trace_id,
            "event": "llm_failed",
            "error": repr(e),
        })

        raise