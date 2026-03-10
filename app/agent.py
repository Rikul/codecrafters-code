import os
import sys

from openai import OpenAI
from app.tools.read_file import read_file, read_file_tool_spec

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")

class Agent:

    def __init__(self):
        if not API_KEY:
                raise RuntimeError("OPENROUTER_API_KEY is not set")

        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def start_loop(self, prompt: str):
        
        chat = self.client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=[{"role": "user", "content": prompt}],
            tools=[read_file_tool_spec]
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!", file=sys.stderr)

        print(chat.choices[0].message.content)
