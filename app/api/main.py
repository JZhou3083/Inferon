from fastapi import FastAPI
from pydantic import BaseModel
import time 
from app.services.llm_service import generate_response

app = FastAPI(title = "Inferon Platform", description = "LLM Infra Platform", version = "1.0.0")

# ------------ Request Schema ------------
class GenreateRequest(BaseModel):
    prompt: str

# ------------ Health Check ------------
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ------------ Generate Endpoint ------------
@app.post("/generate")
async def generate(request: GenreateRequest):
    start_time = time.time()
    response = await generate_response(request.prompt)
    end_time = time.time()
    latency = end_time - start_time

    return {
        "response": response,
        "latency": latency
    }