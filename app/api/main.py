from fastapi import FastAPI
from pydantic import BaseModel
import time 
from app.services.llm_service import generate_response
from app.core.logging import logger

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
    start_time = time.time()

    response,cache_hit = await generate_response(request.prompt)

    latency = time.time() - start_time

    logger.info({
        "event": "generate",
        "prompt": request.prompt,
        "response": response,
        "latency": latency,
        "cache_hit": cache_hit
    })

    return {
        "response": response,
        "latency": latency,
        "cache_hit": cache_hit
    }