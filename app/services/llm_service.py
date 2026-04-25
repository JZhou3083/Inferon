import asyncio
import time
from app.cache.redis_cache import get_cache, set_cache
from app.schemas.llm import LLMRequest, LLMResult
from app.core.logging import logger
from openai import AsyncOpenAI

client = AsyncOpenAI(base_url="https://api.deepseek.com")

def build_cache_key(prompt: str) -> str:
    return f"llm:{prompt}"

async def generate_response(request: LLMRequest) -> LLMResult:
    prompt = request.prompt
    trace_id = request.trace_id
    
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

    max_retries = 3
    timeout_seconds = 20
    llm_start = time.time()

    response = None
    last_error = None

    for attempt in range(max_retries):
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=timeout_seconds
            )
            break

        except Exception as e:
            last_error = e
            await asyncio.sleep(1)

    if response is None:
        logger.warning({
            "trace_id": trace_id,
            "event": "llm_failed",
            "error": repr(last_error)
        })
        raise Exception("LLM call failed after retries")

    output = response.choices[0].message.content

    logger.info({
        "trace_id": trace_id,
        "event": "llm_success",
        "llm_latency": time.time() - llm_start,
        "response_len": len(output),
        "attempts": attempt + 1
    })

    set_cache(cache_key, output)

    return LLMResult(text=output, cache_hit=False)