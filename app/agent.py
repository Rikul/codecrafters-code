import sys
import json

from app.client import Client
from app.tools.tool_calls import run_tool, read_file_tool_spec


class Agent:

    def __init__(self):
        self.client = Client().get_client()

    def start_loop(self, message: str):
        
        while True:

            chat = self.client.chat.completions.create(
                model="anthropic/claude-haiku-4.5",
                messages=[{"role": "user", "content": message}],
                tools=[read_file_tool_spec]
            )

            if not chat.choices or len(chat.choices) == 0:
                raise RuntimeError("no choices in response")

            print(f"chat.choices: {chat.choices}", file=sys.stderr)
            choice = chat.choices[0]

            if choice.message.tool_calls is not None:

                for tool_call in choice.message.tool_calls:

                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    result = {}
                    result["role"] = "tool"
                    result["tool_call_id"] = tool_call.id
                    result["content"] = run_tool(tool_name=tool_name, tool_args=tool_args)

                    message += json.dumps(result)
            else:
                print(chat.choices[0].message.content)
                break

