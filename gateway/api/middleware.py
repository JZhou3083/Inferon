from fastapi import Request
import uuid

async def add_trace_id(request: Request, call_next):

    trace_id = str(uuid.uuid4())

    request.state.trace_id = trace_id

    response = await call_next(request)

    response.headers["X-Trace-ID"] = trace_id

    return response