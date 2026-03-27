from fastapi import FastAPI
from pydantic import BaseModel
import time 
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

# ------------ Request Schema ------------
class GenerateRequest(BaseModel):
    prompt: str

# ------------ Health Check ------------
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ------------ Generate Endpoint ------------
@app.post("/generate")
async def generate(request: GenerateRequest):
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        response, cache_hit = await generate_response(request.prompt)

    if cache_hit:
        CACHE_HIT.inc()
    else:
        CACHE_MISS.inc()

    logger.info({
        "event": "generate",
        "prompt": request.prompt,
        "response": response,
        "cache_hit": cache_hit
    })

    return {
        "response": response,
        "cache_hit": cache_hit
    }

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")