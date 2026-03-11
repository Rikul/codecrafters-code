import sys
import json

from app.client import Client
from app.tools.tool_calls import run_tool, tool_specs
from app.config import Config
from app.helpers import load_system_context

class Agent:

    def __init__(self):
        self.client = Client().get_client()

    def send_system_context(self):
        system_context = load_system_context()
        if system_context:
            return self.client.chat.completions.create(
                model=Config.get_model(),
                messages=[{"role": "system", "content": system_context}]
            )
    
    def start_loop(self, message: str):

        self.send_system_context()
        
        messages = [{"role": "user", "content": message}]
        while True:

            chat = self.client.chat.completions.create(
                model=Config.get_model(),
                messages=messages,
                tools=[ tool_specs["read_file"], tool_specs["write_file"], 
                        tool_specs["bash"], tool_specs["web_fetch"]]
            )

            if not chat.choices or len(chat.choices) == 0:
                raise RuntimeError("no choices in response")

            assistant_message = chat.choices[0].message
            messages.append(assistant_message)

            print(f"assistant: {assistant_message.content}", file=sys.stderr)

            if assistant_message.tool_calls is not None:

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
                print(assistant_message.content)
                break

