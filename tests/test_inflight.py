import asyncio
import pytest
from inferon.orchestration.in_flight import get_or_create, resolve, fail
from inferon.orchestration.in_flight import _in_flight  # 注意是 _in_flight
@pytest.mark.asyncio
async def test_deduplication():
    call_count = 0
    key = "test_key"
    
    async def slow_coro():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return "result"
    
    # 获取 10 个 Future（不执行 coroutine）
    futures = [await get_or_create(key) for _ in range(10)]
    
    # 第一个请求执行真正的逻辑
    async def first_execution():
        result = await slow_coro()
        resolve(key, result)
        return result
    
    # 启动第一个执行（不需要 await 它）
    first_task = asyncio.create_task(first_execution())
    
    # 所有其他请求等待结果
    results = await asyncio.gather(*[asyncio.ensure_future(f) for f in futures])
    
    assert call_count == 1  # 只执行了一次
    assert all(r == "result" for r in results)
    
    # 清理
    _in_flight.pop(key, None)

@pytest.mark.asyncio
async def test_failure_propagation():
    key = "fail_key"
    
    # 获取多个 Future
    futures = [await get_or_create(key) for _ in range(5)]
    
    # 第一个执行失败
    async def failing_execution():
        await asyncio.sleep(0.1)
        raise ValueError("LLM call failed")
    
    first_task = asyncio.create_task(failing_execution())
    
    # 等待并捕获异常
    try:
        await first_task
    except ValueError:
        fail(key, ValueError("LLM call failed"))
    
    # 所有其他 Future 应该抛出相同的异常
    for future in futures:
        with pytest.raises(ValueError):
            await future
    
    # 清理
    _in_flight.pop(key, None)

@pytest.mark.asyncio
async def test_concurrent_identical_keys():
    """10个并发请求同一个key，只有一个真正执行"""
    call_count = 0
    key = "concurrent_key"
    
    async def expensive_op():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.05)
        return "shared_result"
    
    async def worker():
        future = await get_or_create(key)
        if future.done():
            return future.result()
        else:
            # 第一个 worker 执行
            result = await expensive_op()
            resolve(key, result)
            return result
    
    # 10个并发worker
    results = await asyncio.gather(*[worker() for _ in range(10)])
    
    assert call_count == 1
    assert all(r == "shared_result" for r in results)
    
    _in_flight.pop(key, None)