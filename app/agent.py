import sys
import json

from app.client import Client
from app.tools.tool_calls import run_tool, read_file_tool_spec


class Agent:

    def __init__(self):
        self.client = Client().get_client()

    def start_loop(self, prompt: str):
        
        chat = self.client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=[{"role": "user", "content": prompt}],
            tools=[read_file_tool_spec]
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print(f"chat.choices: {chat.choices}", file=sys.stderr)

        for choice in chat.choices:

            if choice.message.tool_calls is not None:
            #if choice.message.role == "assistant" and len(choice.message.tool_calls) > 0:

                for tool_call in choice.message.tool_calls:
                    #print(f"tool_call: {tool_call} tool_name: {tool_call.function.name} ", file=sys.stderr)

                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    result = run_tool(tool_name=tool_name, tool_args=tool_args)
                    print(result)

            else:
                print(chat.choices[0].message.content)

