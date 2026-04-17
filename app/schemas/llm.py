from pydantic import BaseModel

class LLMRequest(BaseModel):
    prompt: str
    trace_id: str


class LLMResult(BaseModel):
    text: str
    cache_hit: bool
    latency: float | None = None