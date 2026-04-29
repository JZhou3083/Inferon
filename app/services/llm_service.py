import asyncio
import time
import hashlib

from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type
)

from app.cache.redis_cache import get_cache, set_cache
from app.schemas.llm import LLMResult
from app.core.logging import logger


# =========================================================
# CONFIG / GLOBALS
# =========================================================

# OpenAI-compatible client (DeepSeek endpoint)
client = AsyncOpenAI(base_url="https://api.deepseek.com")

# Limits concurrent LLM calls to avoid overload / rate limits
semaphore = asyncio.Semaphore(5)

# Placeholder for future "in-flight request deduplication"
# (prevents multiple identical cache-miss requests hitting LLM)
in_flight: dict[str, asyncio.Future] = {}


# =========================================================
# CACHE KEY
# =========================================================

def build_cache_key(prompt: str) -> str:
    """
    Creates a stable hash-based cache key for a prompt.

    We hash instead of storing raw prompts to:
    - avoid huge Redis keys
    - normalize long prompts safely
    """
    hashed = hashlib.sha256(prompt.encode()).hexdigest()
    return f"llm:{hashed}"


# =========================================================
# LLM CALL (LOW-LEVEL)
# =========================================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(min=1, max=8),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def _retryable_llm_call(prompt: str, timeout_seconds: int):
    """
    Raw LLM API call with:
    - retry (transient failures, rate limits, etc.)
    - timeout protection (prevents hanging requests)
    """
    return await asyncio.wait_for(
        client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        ),
        timeout=timeout_seconds
    )


# =========================================================
# EXECUTION LAYER (CONCURRENCY CONTROL)
# =========================================================

async def _execute_llm(prompt: str, timeout_seconds: int):
    """
    Single responsibility:
    - enforce concurrency limit (semaphore)
    - delegate retry + API call below
    """
    async with semaphore:
        return await _retryable_llm_call(prompt, timeout_seconds)


# =========================================================
# PUBLIC API (ORCHESTRATION LAYER)
# =========================================================

async def generate_response(prompt: str, trace_id: str) -> LLMResult:
    """
    Main entry point for LLM generation.

    Flow:
    1. Check Redis cache
    2. If miss → call LLM (with retry + semaphore)
    3. Log metrics
    4. Store result in cache
    5. Return response
    """

    cache_key = build_cache_key(prompt)

    # -------------------------
    # 1. CACHE LOOKUP
    # -------------------------
    cached = get_cache(cache_key)
    if cached:
        logger.info({
            "trace_id": trace_id,
            "event": "cache_hit",
            "cache_key": cache_key[-8:]
        })
        return LLMResult(text=cached, cache_hit=True)

    logger.info({
        "trace_id": trace_id,
        "event": "cache_miss",
        "cache_key": cache_key[-8:]
    })

    # -------------------------
    # 2. LLM CALL
    # -------------------------
    timeout_seconds = 20
    llm_start = time.time()

    try:
        response = await _execute_llm(prompt, timeout_seconds)

    except Exception as e:
        logger.warning({
            "trace_id": trace_id,
            "event": "llm_failed",
            "error": repr(e)
        })
        raise Exception("LLM call failed after retries") from e

    output = response.choices[0].message.content

    # -------------------------
    # 3. METRICS LOGGING
    # -------------------------
    logger.info({
        "trace_id": trace_id,
        "event": "llm_success",
        "llm_latency": time.time() - llm_start,
        "response_len": len(output),
    })

    # -------------------------
    # 4. CACHE WRITE
    # -------------------------
    set_cache(cache_key, output)

    # -------------------------
    # 5. RESPONSE
    # -------------------------
    return LLMResult(text=output, cache_hit=False)