from abc import ABC, abstractmethod

from .client import Client
from .startup import load_system_context


class Agent(ABC):

    def __init__(self, max_iterations: int = 100) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
        self.max_iterations = max_iterations

        system_context = load_system_context()
        if system_context:
            self.messages.append({"role": "system", "content": system_context})

    @abstractmethod
    async def agent_loop(self, message: str, metadata: dict = None) -> None:
        pass
