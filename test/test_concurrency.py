import asyncio
import httpx

async def send(i):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "http://localhost:8000/generate",
            json={"prompt": f"test {i}"}
        )
        print(i, r.status_code)

async def main():
    await asyncio.gather(*(send(i) for i in range(50)))

asyncio.run(main())