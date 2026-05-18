# benchmark.py
import asyncio
import time
import aiohttp

async def send_request(session, prompt):
    start = time.time()
    async with session.post("http://localhost:8000/generate", json={"prompt": prompt}) as resp:
        await resp.json()
    return time.time() - start

async def main():
    async with aiohttp.ClientSession() as session:
        # 并发10个请求，对比有/无semaphore的延迟分布
        tasks = [send_request(session, f"Prompt {i}") for i in range(50)]
        latencies = await asyncio.gather(*tasks)
        print(f"p50: {sorted(latencies)[5]:.2f}s, p99: {sorted(latencies)[9]:.2f}s")

asyncio.run(main())