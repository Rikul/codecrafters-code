from openai import AsyncOpenAI
import os

API_KEY = os.environ.get("LLM_API_KEY")
BASE_URL = os.environ.get("LLM_BASE_URL", default="https://openrouter.ai/api/v1")

class Client:

    def __init__(self, api_key: str = API_KEY, base_url: str = BASE_URL):
        if not API_KEY and not api_key:
            raise RuntimeError("API_KEY is not set")

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def get_client(self):
        return self.client