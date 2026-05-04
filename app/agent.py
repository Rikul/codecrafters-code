from abc import ABC, abstractmethod

from .client import Client
from .startup import load_system_context

MAX_CONTEXT_MESSAGES = 100


class Agent(ABC):

    def __init__(self, max_iterations: int = 250) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
        self.max_iterations = max_iterations

        system_context = load_system_context()
        if system_context:
            self.messages.append({"role": "system", "content": system_context})

    def _trim_messages(self) -> None:
        """Keep system message + last MAX_CONTEXT_MESSAGES messages."""
        if self.messages and self.messages[0]["role"] == "system":
            system = self.messages[:1]
            rest = self.messages[1:]
        else:
            system = []
            rest = self.messages

        if len(rest) > MAX_CONTEXT_MESSAGES:
            self.messages = system + rest[-MAX_CONTEXT_MESSAGES:]

    @staticmethod
    def _serialize_assistant_msg(msg) -> dict:
        d = {"role": msg.role, "content": msg.content}
        if msg.tool_calls:
            d["tool_calls"] = [tc.model_dump() for tc in msg.tool_calls]
        reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)
        if reasoning is not None:
            d["reasoning_content"] = reasoning
        return d

    @abstractmethod
    async def agent_loop(self, message: str, metadata: dict = None) -> None:
        pass
