# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Inferon is a lightweight LLM routing/orchestration layer (conceptually similar to LiteLLM, not an inference runtime like vLLM). It sits in front of one or more LLM providers and adds caching, request coalescing, retries, and observability. It's an in-progress learning/portfolio project — expect stub logic (e.g. `Router.route` always returns `"deepseek"`) rather than production-complete features.

## Running the service

```bash
docker compose up --build -d   # starts redis + app (uvicorn gateway.api.main:app on :8000)
docker compose down
```

The app depends on a `redis` service reachable at host `redis:6379` (see `inferon/cache/redis_cache.py` — the hostname is hardcoded to the docker-compose service name, so the API will not run correctly outside the compose network without changing that host). `OPENAI_API_KEY` must be set via `.env` (loaded through `env_file` in `docker-compose.yml`) since `DeepSeekLLM` uses the OpenAI SDK pointed at `https://api.deepseek.com`.

Note: `dockerfile`'s CMD (`app.api.main:app`) does not match the actual package layout (`gateway.api.main:app`, as used by docker-compose's `command:`). Use the docker-compose command, not the Dockerfile CMD, to run the service.

## Tests

```bash
pytest tests/test_inflight.py   # only file that's a real, self-contained pytest suite
```

`tests/test_cache.py` requires `client` and `cache` pytest fixtures that do not exist yet anywhere in the repo (no `conftest.py`) — running it will error on fixture setup, not a code bug. `tests/test.py` and `tests/test_concurrency.py` are standalone async load-test scripts (they call `asyncio.run()` at import time) meant to be run directly against a live server, e.g. `python tests/test_concurrency.py` — not part of the pytest suite.

## Architecture

Request flow (see `ARCHITECTURE.md` for the design-decision rationale in more detail):

```
gateway/api (FastAPI)
  → middleware assigns trace_id
  → routes/generate.py
      → inferon.routing.router.Router      (pick provider)
      → inferon.orchestration.executor.execute()
          1. inferon.cache.redis_cache      (cache lookup by sha256(prompt))
          2. inferon.orchestration.in_flight (in-process request coalescing)
          3. provider.complete()            (inferon.llms.*, retried via tenacity)
          4. cache write + resolve in-flight future
      → inferon.observability.{logging,metrics}
```

Key modules:
- `gateway/api/` — FastAPI app, routes (`/generate`, `/health`, `/metrics`), trace-id middleware.
- `inferon/routing/router.py` — provider selection; currently a placeholder (always `deepseek`).
- `inferon/orchestration/executor.py` — the core pipeline: cache check → in-flight dedup → provider call (behind a global `asyncio.Semaphore(5)`, `tenacity` retry with exponential backoff) → cache write.
- `inferon/orchestration/in_flight.py` — module-level dict of `asyncio.Future`s keyed by cache key, used to coalesce concurrent identical requests into a single upstream call. Each entry has a 30s self-cleanup timeout.
- `inferon/cache/redis_cache.py` — Redis-backed cache; keys are `llm:{sha256(prompt)}`, TTL 300s.
- `inferon/llms/` — provider adapters implementing `BaseLLM.complete()`; currently only `DeepSeekLLM` (via `AsyncOpenAI` client against DeepSeek's OpenAI-compatible endpoint).
- `inferon/observability/` — JSON-structured logging (`logger.info({...dict...})` pattern, not string messages) and Prometheus counters/histograms exposed at `/metrics`.
- `inferon/schemas/` — split into `api/` (FastAPI request/response models) and `internal/` (models passed between internal layers, e.g. `LLMResult`).

When adding a new LLM provider: implement `BaseLLM` in `inferon/llms/`, then register it in `Router.__init__`'s `self.providers` dict.
