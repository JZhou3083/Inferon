from fastapi import APIRouter, Request
import time
from inferon.schemas.api.generate import GenerateRequest, GenerateResponse
from inferon.routing.router import Router
from inferon.orchestration.executor import execute
from inferon.observability.logging import logger
from inferon.observability.metrics import (
    REQUEST_COUNTER,
    REQUEST_LATENCY,
    CACHE_HIT,
    CACHE_MISS,
)

router = APIRouter()

llm_router = Router()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    http_request: Request,
):

    trace_id = http_request.state.trace_id

    start_time = time.time()

    REQUEST_COUNTER.inc()

    # ----------------------------------------
    # routing
    # ----------------------------------------

    provider_name = llm_router.route(
        request.model_dump()
    )

    provider = llm_router.get_provider(
        provider_name
    )

    # ----------------------------------------
    # execution
    # ----------------------------------------

    with REQUEST_LATENCY.time():

        result = await execute(
            provider=provider,
            prompt=request.prompt,
            trace_id=trace_id,
        )

    latency = time.time() - start_time

    # ----------------------------------------
    # metrics
    # ----------------------------------------

    if result.cache_hit:
        CACHE_HIT.inc()
    else:
        CACHE_MISS.inc()

    logger.info({
        "trace_id": trace_id,
        "event": "generate",
        "provider": provider_name,
        "latency": latency,
        "cache_hit": result.cache_hit,
        "prompt_len": len(request.prompt),
        "response_len": len(result.text),
    })

    # ----------------------------------------
    # response
    # ----------------------------------------

    return GenerateResponse(
        response=result.text,
        cache_hit=result.cache_hit,
    )