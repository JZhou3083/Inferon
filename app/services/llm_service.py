import asyncio
import time
import hashlib
from app.cache.redis_cache import get_cache, set_cache
from app.schemas.llm import LLMResult
from app.core.logging import logger
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
# todo: add in-flight request deduplication to avoid thundering herd on cache miss. This is a bit more complex and can be added in a future iteration.
client = AsyncOpenAI(base_url="https://api.deepseek.com")
semaphore = asyncio.Semaphore(5)

def build_cache_key(prompt: str) -> str:
    hashed = hashlib.sha256(prompt.encode()).hexdigest()
    return f"llm:{hashed}"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(min=1, max=8),
    retry=retry_if_exception_type(Exception),  # keep simple for now
    reraise=True
)
async def _retryable_llm_call(prompt: str, timeout_seconds: int):
    return await asyncio.wait_for(
        client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        ),
        timeout=timeout_seconds
    )

async def generate_response(prompt: str, trace_id: str) -> LLMResult:
    # Check if the response is already cached
    cache_key = build_cache_key(prompt)

    cached = get_cache(cache_key)
    if cached:
        logger.info({
            "trace_id": trace_id,
            "event": "cache_hit",
            "cache_key": cache_key[-8:]
        })
        return LLMResult(text=cached, cache_hit=True)
    # 🔹 2. cache miss
    logger.info({
        "trace_id": trace_id,
        "event": "cache_miss",
        "cache_key": cache_key[-8:]
    })

    timeout_seconds = 20
    llm_start = time.time()

    response = None
    
    try:
        async with semaphore:  
            response = await _retryable_llm_call(prompt, timeout_seconds)


    except Exception as e:
        logger.warning({
            "trace_id": trace_id,
            "event": "llm_failed",
            "error": repr(e)
        })
        raise Exception("LLM call failed after retries")

    output = response.choices[0].message.content

    logger.info({
        "trace_id": trace_id,
        "event": "llm_success",
        "llm_latency": time.time() - llm_start,
        "response_len": len(output),
    })

    set_cache(cache_key, output)

    return LLMResult(text=output, cache_hit=False)