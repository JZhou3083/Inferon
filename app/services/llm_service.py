import asyncio
from app.cache.redis_cache import get_cache, set_cache

def build_cache_key(prompt: str) -> str:
    return f"llm:{prompt}"

async def generate_response(prompt: str) -> tuple[str, bool]:
    # Check if the response is already cached
    cache_key = build_cache_key(prompt)
    cached = get_cache(cache_key)
    if cached:
        return cached, True

    # Simulate a time-consuming operation (e.g., calling an LLM API)
    await asyncio.sleep(2)  # Simulating latency
    response = f"Echo: '{prompt}'"
    
    # Cache the response
    set_cache(cache_key, response)
    
    return response, False