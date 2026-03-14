import sys
import json

from app.client import Client
from app.tools.tool_calls import run_tool, tool_registry
from app.config import Config
from app.helpers import load_system_context
from app.display import console, log
from rich.markdown import Markdown
from app.display import ask_permission

class Agent:
    # Hardcode max iterations to prevent infinite loops during development
    MAX_ITERATIONS = 100

    def __init__(self, auto_approve: bool = False) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
        self.auto_approve = auto_approve
        
        system_context = load_system_context()
        if system_context:
            self.messages.append({"role": "system", "content": system_context})

    async def agent_loop(self, message: str) -> None:
        
        self.messages.append({"role": "user", "content": message})
        tool_specs = [tool["spec"] for tool in tool_registry.values()]

        iteration = 0
        while iteration < self.MAX_ITERATIONS:
            iteration += 1

            chat = self.client.chat.completions.create(
                model=Config.get_model(),
                messages=self.messages,
                tools=tool_specs
            )

            if not chat.choices or len(chat.choices) == 0:
                raise RuntimeError("no choices in response")

            assistant_message = chat.choices[0].message
            self.messages.append(assistant_message)


            if assistant_message.tool_calls is not None:
    
                if assistant_message.content is not None and assistant_message.content.strip() != "":
                    console.print(Markdown(assistant_message.content))

                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    result = ""

                    if not self.auto_approve and not ask_permission(tool_name, tool_args):
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": "User denied permission to run this tool"
                        })
                        continue

                    try:
                        result = run_tool(tool_name=tool_name, tool_args=tool_args)
                    except Exception as e:
                        result = f"Error running tool {tool_name}: {str(e)}"
                        log.error(result)

                    self.messages.append({
                        "role": "tool", 
                        "tool_call_id": tool_call.id, 
                        "name": tool_name, 
                        "content": result
                    })                  

            else:
                if assistant_message.content:
                    console.print(Markdown(assistant_message.content))
                break

