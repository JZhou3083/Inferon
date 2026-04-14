# LLM Infra Platform

A production-oriented LLM infrastructure platform designed to serve multiple applications with scalable inference, optimization, and observability.

---

## 🚀 Overview

This project simulates a real-world **LLM infrastructure layer** used in modern enterprises.

Instead of building a single AI application, this platform acts as a **centralized service** that multiple downstream applications can rely on for:

* LLM inference
* request optimization (caching, batching)
* latency and performance tracking
* unified deployment and monitoring

---

## 🎯 Problem It Solves

In production environments, directly integrating LLMs into each application leads to:

* duplicated logic across teams
* high and uncontrolled API costs
* poor latency under load
* lack of observability
* no centralized governance

This platform addresses these challenges by introducing a **shared LLM infrastructure layer**.

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
        ├── Orchestration Layer
        ├── Inference Layer
        ├── Optimization Layer (Cache, Batching)
        └── Observability & MLOps
        │
        ▼
LLM Provider / Model Backend
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

## ⚙️ Key Features (Planned)

* ✅ Unified LLM API service
* ✅ Async request handling
* ✅ Response caching (Redis)
* ✅ Latency & metrics tracking
* ✅ LLM model Integration
* ⏳ Request batching (planned)
* ⏳ vLLM & LMcache
* ⏳ Model backend abstraction (OpenAI / local / vLLM)

---

## 🧠 Design Principles

* **Separation of concerns** (API vs model logic vs infra)
* **Pluggable model backend**
* **Scalable architecture**
* **Production-first mindset**

---

## 🛠 Tech Stack

* FastAPI
* Python (async)
* Redis
* Docker / Docker Compose
* (Planned) MLflow, CI/CD

---

## 📌 Future Work

* vLLM integration for high-performance inference
* distributed processing (optional)
* multi-tenant support
* observability dashboard
* cost tracking & optimization

---

## 📖 Why This Project?

This project covers topics of:

* ML Infrastructure Engineering
* AI Platform Engineering
* MLOps & Production AI Systems
---

## Current logs
How to Run& Stop both redis and app services: 
* 'docker compose up --build -d'
* 'docker compose down'

cache → logging → metrics → tracing → scaling → AI（LLM integration / RAG / agent）