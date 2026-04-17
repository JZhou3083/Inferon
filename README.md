# LLM Infra Platform

A production-oriented LLM infrastructure platform designed to serve multiple applications with scalable inference, optimization, and observability.

---

## 🚀 Overview

This project implements a **modular LLM infrastructure layer** inspired by production systems used in modern AI companies.

It is designed to serve as a shared backend for multiple applications requiring:

- LLM inference
- request optimization (caching, batching)
- observability (metrics, logging)
- scalable serving architecture (future)

---

## 🏗 Architecture

```
Clients (Apps)
   │
   ├── App A
   ├── App B
   └── App C
        │
        ▼
LLM Infra Platform (this project)
        │
        ├── API Layer (FastAPI)
        ├── Observability Layer(logging, metrics)
        ├── Optimization Layer (cache, batching)
        ├── Inference Layer
        └── Future: Agent + Distributed Layer 
        │
        ▼
LLM Provider (OpenAI/local/vLLM)
```

---

## 📦 Project Structure

```
llm-infra-platform/
│
├── app/
│   ├── api/                # FastAPI routes (entry point)
│   ├── core/               # config, logging, utilities
│   ├── services/           # LLM interaction logic
│   ├── metrics/            # Observability metrics 
│   ├── cache/              # caching layer (Redis)
│   └── models/             # request/response schemas
│
├── tests/                  # unit & integration tests
│
├── docker/                 # Docker-related configs
│
├── .github/workflows/      # CI/CD pipelines
│
├── docker-compose.yml      # local orchestration (app + Redis)
│
└── README.md
```

---

## ⚙️ Key Features

### Implemented
- FastAPI LLM service
- Redis caching layer
- Structured logging with trace_id
- Metrics (latency, cache hit/miss)
- Dockerized local environment

### In Progress
- Request tracing (context propagation)
- Batching prototype (static batching)

### Planned
- Continuous batching (vLLM-style scheduler)
- Agentic execution layer (SGLang-style)
- Distributed inference (Ray)
- External KV cache (LMCache)

---

## 🧠 Design Principles

- Separation of concerns (API / infra / inference)
- Observable-by-default (metrics + logging)
- Pluggable model backend
- Scalable system design mindset

---

## 🛠 Tech Stack

- FastAPI
- Python (async)
- Redis
- Docker / Docker Compose
- Prometheus metrics

---

## 📖 Why This Project?

This project explores real-world topics in:

- LLM Infrastructure Engineering
- AI Platform Design
- MLOps systems
- Scalable inference architectures

---

## 🚀 How to Run

```bash
docker compose up --build -d
docker compose down