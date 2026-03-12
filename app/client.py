from openai import OpenAI
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", default="https://openrouter.ai/api/v1")

class Client:

    def __init__(self, api_key: str = API_KEY, base_url: str = BASE_URL):
        if not API_KEY and not api_key:
            raise RuntimeError("API_KEY is not set")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def get_client(self):
        return self.client