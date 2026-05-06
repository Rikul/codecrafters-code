from abc import ABC, abstractmethod

from .client import Client

MAX_CONTEXT_MESSAGES = 100


class Agent(ABC):

    def __init__(self, max_iterations: int = 250) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
        self.max_iterations = max_iterations

    def _trim_messages(self) -> None:
        if len(self.messages) > MAX_CONTEXT_MESSAGES:
            self.messages = self.messages[-MAX_CONTEXT_MESSAGES:]

    @staticmethod
    def _serialize_assistant_msg(msg) -> dict:
        d = {"role": msg.role, "content": msg.content}
        if msg.tool_calls:
            d["tool_calls"] = [tc.model_dump() for tc in msg.tool_calls]
            raw = msg.model_dump()
            reasoning = raw.get("reasoning_content") or raw.get("reasoning")
            if reasoning:
                d["reasoning_content"] = reasoning
        return d

    @abstractmethod
    async def agent_loop(self, message: str, metadata: dict = None) -> None:
        pass
