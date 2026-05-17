# LLM Infra Platform

A production-oriented LLM infrastructure platform designed to serve multiple applications with scalable inference, optimization, and observability.

---

## 🚀 Overview

This project implements a **modular LLM infrastructure layer** inspired by production systems used in modern AI companies.

It is designed to serve as a shared backend for multiple applications requiring:

- LLM models
- observability (metrics, logging)
- scalable serving architecture (future)

---

## 🏗 Architecture

```
API Layer
(app/api)
    ↓
Orchestration Layer
(orchestration/in_flight.py)
    ↓
Routing Layer
(routing/router.py)
    ↓
Provider Layer
(providers/)
    ↓
External LLMs
    ↓
Observability + Cache (side systems)
```

---

## 📦 Project Structure

```
Inferon/
├── README.md
├── docker-compose.yml
├── dockerfile
├── gateway # 
│   └── api
├── inferon #逻辑
│   ├── cache
│   ├── llms
│   ├── observability
│   ├── orchestration
│   ├── routing
│   └── schemas
├── infra # 实际工具
├── requirements.txt
└── tests
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