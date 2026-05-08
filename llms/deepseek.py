import asyncio

from openai import AsyncOpenAI

from llms.base import BaseLLM


class DeepSeekLLM(BaseLLM):

    name = "deepseek"

    def __init__(self):

        self.client = AsyncOpenAI(
            base_url="https://api.deepseek.com",
        )

        self.model = "deepseek-chat"

    async def complete(
        self,
        *,
        prompt: str,
        timeout: int,
    ) -> str:

        response = await asyncio.wait_for(

            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=2048,
            ),

            timeout=timeout,
        )

        return response.choices[0].message.content