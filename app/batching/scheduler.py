import asyncio
from typing import List, Tuple
from app.schemas.llm import LLMResult
from app.services.llm_service import generate_response

class BatchScheduler:
    def __init__(self, batch_size: int = 4, flush_interval: float = 0.05):
        self.queue: List[Tuple[str, str, asyncio.Future]] = []
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.lock = asyncio.Lock()

        # 启动后台 worker
        asyncio.create_task(self.worker_loop())

    async def submit(self, prompt: str, trace_id: str) -> LLMResult:
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        async with self.lock:
            self.queue.append((prompt, trace_id, future))

        return await future

    async def worker_loop(self):
        while True:
            await asyncio.sleep(self.flush_interval)

            async with self.lock:
                if not self.queue:
                    continue

                batch = self.queue[:self.batch_size]
                self.queue = self.queue[self.batch_size:]

            # 拆 batch
            prompts = [item[0] for item in batch]
            trace_ids = [item[1] for item in batch]
            futures = [item[2] for item in batch]

            # ⚠️ v1：简单版本（逐个调用）
            # 先保证 pipeline 正确，后面再优化成真正 batch
            results = []
            for prompt, trace_id in zip(prompts, trace_ids):
                result = await generate_response(prompt, trace_id)
                results.append(result)

            # 回填 future
            for future, result in zip(futures, results):
                if not future.done():
                    future.set_result(result)