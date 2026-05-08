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
├── app
│   └── api
│       ├── main.py
│       ├── middleware.py
│       └── routes
│           ├── generate.py
│           ├── health.py
│           └── metrics.py
├── cache
│   └── redis_cache.py
├── docker-compose.yml
├── dockerfile
├── llms
│   ├── base.py
│   └── deepseek.py
├── observability
│   ├── logging.py
│   └── metrics.py
├── orchestration
│   └── in_flight.py
├── requirements.txt
├── routing
│   └── router.py
├── schemas
│   ├── api
│   │   └── generate.py
│   └── internal
│       └── chat.py
└── tests
    └── test_concurrency.py
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

Inferon其实是多模型多用户的协调曾，类似LiteLLM而不是vLLM（一个是服务模型的路由层，一个是推理runtime 层，接下来的思路是需要调整的。还有个是Helicone专门observabilityu的项目也值得看一下。）

学习顺序：
🧭 第一阶段：先看整体设计（必须）
1️⃣ 首先看这个文件（最重要）

👉 ARCHITECTURE.md

这里会告诉你：

LiteLLM 的整体分层
request flow（请求怎么走）
proxy vs core 的关系
router 怎么参与决策

📌 目标：

建立“脑内系统图”，否则你后面看代码会完全碎片化。

2️⃣ 再看 README.md

👉 不是为了用，而是为了理解产品边界

重点看：

支持哪些 providers
OpenAI compatibility 是怎么定义的
proxy / SDK 的区别
🧠 第二阶段：理解核心请求路径（最关键）

你要搞清楚一句话：

一个请求是怎么从 API 变成某个 LLM provider 调用的？

3️⃣ 必看入口文件
👉 litellm/main.py

这是核心入口之一：

chat/completions 入口
request normalization
route 到 model layer

📌 你要重点找：

request 是怎么标准化的
model 是怎么被选中的
4️⃣ Proxy 层（非常重要）

👉 litellm/proxy/

这里是 LiteLLM 的“产品核心”

你要重点看：

proxy_server.py（或类似入口）
router.py
auth / proxy_auth/
scheduler.py

📌 你要理解：

“为什么 LiteLLM 可以当 OpenAI API 替身？”

答案就在 proxy 层。

🔀 第三阶段：理解“多模型路由”

这是 LiteLLM 的核心竞争力之一

5️⃣ 路由系统（必读）

👉 router.py
👉 router_strategy/
👉 router_utils/

你要搞清楚：

model fallback 怎么做
load balancing 怎么做
tag routing 怎么做
cost-based routing 怎么做

📌 核心思想：

一个 request ≠ 一个 model
而是 → 一个 policy → 多个候选 model

🤖 第四阶段：Provider 适配层（理解扩展能力）
6️⃣ 看 llms/

👉 litellm/llms/

这里是所有 provider adapter：

你会看到类似：

OpenAI
Azure
Anthropic
Bedrock
Google GenAI

📌 你要理解：

“统一接口 = adapter pattern”

核心设计就是：

BaseLLM
  ├── OpenAI
  ├── Anthropic
  ├── Gemini
  ├── Bedrock
🧱 第五阶段：增强能力（进阶）
7️⃣ 这些目录属于“产品能力层”

建议按顺序看：

🔹 caching/

👉 请求缓存怎么做

🔹 compression/

👉 prompt compression（成本优化）

🔹 rag/

👉 retrieval augmentation

🔹 batch_completion/

👉 batch inference

🔹 vector_stores/

👉 向量数据库接口

📌 这一层的本质是：

“LLM 应用能力插件化”

🧩 第六阶段：工程化能力（最后看）

这些不是核心，但很“工业级”：

proxy_auth/ → 鉴权系统
secret_managers/ → secret 管理
budget_manager.py → cost control
_logging.py → observability
evals/ → eval framework
🧠 建议的学习顺序（非常重要）

如果你按这个顺序读，会非常顺：

1. ARCHITECTURE.md
2. README.md
3. main.py
4. proxy/
5. router.py + router_strategy/
6. llms/
7. caching/
8. rag/
9. integrations/