import asyncio
from app.cache.redis_cache import get_cache, set_cache
from app.core.logging import logger
from openai import OpenAI

client = OpenAI(base_url="https://api.deepseek.com")

def build_cache_key(prompt: str) -> str:
    return f"llm:{prompt}"

async def generate_response(prompt: str, trace_id: str) -> tuple[str, bool]:
    # Check if the response is already cached
    cache_key = build_cache_key(prompt)

    cached = get_cache(cache_key)
    if cached:
        logger.info({
            "trace_id": trace_id,
            "event": "cache_hit",
            "cache_key": cache_key
        })
        return cached, True
    # 🔹 2. cache miss
    logger.info({
        "trace_id": trace_id,
        "event": "cache_miss",
        "cache_key": cache_key
    })

    # 🔹 3. LLM call start
    logger.info({
        "trace_id": trace_id,
        "event": "llm_call_start",
        "prompt": prompt
    })
    max_retries = 3
    timeout_seconds = 10

    for attempt in range(max_retries):
        try:
            logger.info({
                "trace_id": trace_id,
                "event": "llm.call_attempt",
                "attempt": attempt + 1
            })

            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat.completions.create,
                    model="deepseek-chat",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                ),
                timeout=timeout_seconds
            )

            break  # 成功就退出 loop

        except asyncio.TimeoutError:
            logger.warning({
                "trace_id": trace_id,
                "event": "llm.timeout",
                "attempt": attempt + 1
            })

        except Exception as e:
            logger.warning({
                "trace_id": trace_id,
                "event": "llm.error",
                "error": str(e),
                "attempt": attempt + 1
            })

        # 如果还没成功，稍微等一下再 retry
        await asyncio.sleep(1)

    else:
        # 所有 retry 都失败
        raise Exception("LLM call failed after retries")
    output = response.choices[0].message.content

    logger.info({
        "trace_id": trace_id,
        "event": "llm_call_end"
    })

    set_cache(cache_key, output)

    return output, False