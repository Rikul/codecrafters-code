import sys
import json

from app.client import Client
from app.tools.tool_calls import run_tool, tool_registry
from app.config import Config
from app.helpers import load_system_context
from app.display import console, log
from rich.markdown import Markdown

class Agent:
    # Hardcode max iterations to prevent infinite loops during development
    MAX_ITERATIONS = 100

    def __init__(self) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
    
    def start_loop(self, message: str) -> None:
        
        messages = []

        system_context = load_system_context()
        if system_context:
            self.messages.append({"role": "system", "content": system_context})

        self.messages.append({"role": "user", "content": message})
        tools = [tool["spec"] for tool in tool_registry.values()]

       
        iteration = 0
        while iteration < self.MAX_ITERATIONS:
            iteration += 1

            chat = self.client.chat.completions.create(
                model=Config.get_model(),
                messages=self.messages,
                tools=tools
            )

            if not chat.choices or len(chat.choices) == 0:
                raise RuntimeError("no choices in response")

            assistant_message = chat.choices[0].message
            self.messages.append(assistant_message)


            if assistant_message.tool_calls is not None:
    
                if assistant_message.content is not None and assistant_message.content.strip() != "":
                    log.info(f"assistant: {assistant_message.content.strip()}")

                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    result = ""

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
                console.print(Markdown(assistant_message.content))
                break

