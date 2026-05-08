from fastapi import FastAPI

from app.api.routes.generate import router as generate_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router

from app.api.middleware import add_trace_id

app = FastAPI(
    title="Inferon",
    description="LLM Infra Platform",
    version="1.0.0"
)

app.middleware("http")(add_trace_id)

app.include_router(generate_router)
app.include_router(health_router)
app.include_router(metrics_router)