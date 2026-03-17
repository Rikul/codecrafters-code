import json

from app.client import Client
from app.tool_calls import run_tool, tool_registry
from app.config import Config
from app.helpers import load_system_context
from app.display import console, log, ask_permission
from rich.markdown import Markdown

class Agent:

    def __init__(self, max_iterations: int, auto_approve: bool = False, workspace: str = "", silent: bool = False) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
        self.auto_approve = auto_approve
        self.workspace = workspace
        self.max_iterations = max_iterations
        self.silent = silent

        system_context = load_system_context()
        if system_context:
            self.messages.append({"role": "system", "content": system_context})


    async def agent_loop(self, message: str) -> None:
        
        self.messages.append({"role": "user", "content": message})
        tool_specs = [tool["spec"] for tool in tool_registry.values()]

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            log.info("sending message to model...")
            chat = self.client.chat.completions.create(
                model=Config.get_model(),
                messages=self.messages,
                tools=tool_specs,
                response_format={"type": "text"} if self.silent else None
            )

            if not chat.choices or len(chat.choices) == 0:
                raise RuntimeError("no choices in response")

            assistant_message = chat.choices[0].message
            self.messages.append(assistant_message)

            if assistant_message.tool_calls is not None:
    
                if not self.silent and assistant_message.content is not None and assistant_message.content.strip() != "":
                    console.print(Markdown(assistant_message.content))

                for tool_call in assistant_message.tool_calls:

                    try:
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
                        
                        result = run_tool(tool_name=tool_name, tool_args=tool_args, workspace=self.workspace)
 
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
                    if self.silent:
                        print(assistant_message.content)
                    else:
                        console.print(Markdown(assistant_message.content))
                break

