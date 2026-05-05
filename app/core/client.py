from __future__ import annotations

from openai import AsyncOpenAI
import os
from .. import config

class Client:

    def __init__(self, api_key: str = None, base_url: str = None) -> None:
        if api_key is None:
            api_key = os.environ.get("LLM_API_KEY") or config.get("api_key", None)

        if base_url is None:
            base_url = os.environ.get("LLM_BASE_URL") or config.get("base_url", "https://openrouter.ai/api/v1")

        if not api_key:
            raise RuntimeError("LLM_API_KEY is not set")

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def get_client(self):
        return self.client