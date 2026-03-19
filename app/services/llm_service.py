import asyncio
from app.cache.redis_cache import get_cache, set_cache

async def generate_response(prompt: str) -> str:
    # Check if the response is already cached
    cached = get_cache(prompt)
    if cached:
        return cached

    # Simulate a time-consuming operation (e.g., calling an LLM API)
    await asyncio.sleep(2)  # Simulating latency
    response = f"Echo: '{prompt}'"
    
    # Cache the response
    set_cache(prompt, response)
    
    return response