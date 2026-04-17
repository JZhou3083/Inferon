from fastapi import FastAPI, Request
import uuid
from pydantic import BaseModel
import time 
from app.schemas.api import GenerateRequest, GenerateResponse
from app.services.llm_service import generate_response
from app.core.logging import logger
from app.metrics.metrics import (
    REQUEST_COUNTER,
    REQUEST_LATENCY,
    CACHE_HIT,
    CACHE_MISS
)
from prometheus_client import generate_latest
from fastapi.responses import Response

app = FastAPI(title = "Inferon", description = "LLM Infra Platform", version = "1.0.0")

# ------------ Health Check ------------
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ------------ Generate Endpoint ------------
@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, http_request: Request):
    trace_id = http_request.state.trace_id
    start_time = time.time()

    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        result = await generate_response(request.prompt,trace_id= trace_id)
    latency = time.time() - start_time
    if result.cache_hit:
        CACHE_HIT.inc()
    else:
        CACHE_MISS.inc()
    logger.info({
        "trace_id": trace_id,
        "event": "generate",
        "prompt": request.prompt,
        "response": result.text,
        "latency": latency,
        "cache_hit": result.cache_hit
    })

    return GenerateResponse(
        response=result.text,
        cache_hit=result.cache_hit
    )

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = str(uuid.uuid4())

    # 挂到 request 上（全链路用）
    request.state.trace_id = trace_id
    response = await call_next(request)

    # 返回给客户端（很重要）
    response.headers["X-Trace-ID"] = trace_id

    return response
