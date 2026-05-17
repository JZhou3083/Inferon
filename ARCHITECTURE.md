# Inferon Architecture

## Request Flow
1. API层接收请求 → 提取trace_id
2. 编排层检查缓存 → hit直接返回
3. 路由层选择provider（目前round-robin，计划支持cost-based）
4. Provider层调用外部LLM
5. 观测性层记录延迟、token消耗

## Key Design Decisions
- **为什么用Redis做缓存？** 降低重复请求的延迟和成本
- **为什么不用vLLM做runtime？** 当前阶段聚焦路由层，推理runtime是可插拔的
- **semaphore控制并发**：防止单用户打爆整个服务

## Comparison with LiteLLM
- Inferon: 轻量、聚焦路由+观测
- LiteLLM: 企业级、多租户、cost tracking、guardrails

