from abc import ABC, abstractmethod


class BaseLLM(ABC):

    name: str

    @abstractmethod
    async def complete(
        self,
        *,
        prompt: str,
        timeout: int,
    ) -> str:
        pass