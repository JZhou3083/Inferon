from fastapi import APIRouter, Request
import time

from app.schemas.api.generate import GenerateRequest, GenerateResponse
from app.services.llm_service import generate_response
from app.core.logging import logger
from app.metrics.metrics import (
    REQUEST_COUNTER,
    REQUEST_LATENCY,
    CACHE_HIT,
    CACHE_MISS
)

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, http_request: Request):

    trace_id = http_request.state.trace_id

    start_time = time.time()
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        result = await generate_response(
            request.prompt,
            trace_id=trace_id
        )

    latency = time.time() - start_time

    if result.cache_hit:
        CACHE_HIT.inc()
    else:
        CACHE_MISS.inc()

    logger.info({
        "trace_id": trace_id,
        "event": "generate",
        "latency": latency,
        "cache_hit": result.cache_hit,
        "prompt_len": len(request.prompt),
        "response_len": len(result.text)
    })

    return GenerateResponse(
        response=result.text,
        cache_hit=result.cache_hit
    )