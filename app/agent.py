import sys
import json

from app.client import Client
from app.tools.tool_calls import run_tool, read_file_tool_spec


class Agent:

    def __init__(self):
        self.client = Client().get_client()

    def start_loop(self, message: str):
        
        messages = [{"role": "user", "content": message}]
        while True:

            chat = self.client.chat.completions.create(
                model="anthropic/claude-haiku-4.5",
                messages=messages,
                tools=[read_file_tool_spec]
            )

            if not chat.choices or len(chat.choices) == 0:
                raise RuntimeError("no choices in response")

            print(f"chat.choices: {chat.choices}", file=sys.stderr)

            assistant_message = chat.choices[0].message
            messages.append(assistant_message)

            if assistant_message.tool_calls is not None:
                print(f"tool_calls: {assistant_message.tool_calls}", file=sys.stderr)

                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    result = run_tool(tool_name=tool_name, tool_args=tool_args)
                    messages.append({
                        "role": "tool", 
                        "tool_call_id": tool_call.id, 
                        "name": tool_name, 
                        "content": result
                    })                  

            else:
                print(chat.choices[0].message.content)
                break

