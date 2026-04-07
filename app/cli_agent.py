from __future__ import annotations

import json

from . import config
from .client import Client
from .tool_calls import run_tool, all_tool_specs
from .helpers import load_system_context
from .app_logging import log
from .cli import ask_permission

class CliAgent:

    def __init__(self, max_iterations: int = 100, auto_approve: bool = False, silent: bool = False) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
        self.auto_approve = auto_approve or silent
        self.max_iterations = max_iterations
        self.silent = silent

        system_context = load_system_context()
        if system_context:
            self.messages.append({"role": "system", "content": system_context})

    async def agent_loop(self, message: str) -> None:
        
        self.messages.append({"role": "user", "content": message})

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            log.info("chat.completions.create...")
            chat = await self.client.chat.completions.create(
                model=config.get("model", "deepseek/deepseek-v3.2"),
                messages=self.messages,
                tools=all_tool_specs,
                response_format={"type": "text"} if self.silent else None,
                max_tokens=config.get("max_tokens", 16384)
            )

            if not chat.choices or len(chat.choices) == 0:
                raise RuntimeError("no choices in response")

            choice = chat.choices[0]
            assistant_message = choice.message
            finish_reason = getattr(choice, "finish_reason", None)
            if not isinstance(finish_reason, str):
                finish_reason = None

            if assistant_message.tool_calls is not None:
                self.messages.append(assistant_message)

                if not self.silent and assistant_message.content is not None and assistant_message.content.strip() != "":
                    print(assistant_message.content.strip())
                    
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
                                    "content": "User denied permission to run this tool. Ask for permission to run the tool again if you want to try running it."
                                })
                            continue
                        
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

                    log.info(f"{result[:200]}...")

            else:
                if assistant_message.content is not None and assistant_message.content.strip() != "":
                    print(assistant_message.content)

                if finish_reason in ("stop", None):
                    self.messages.append(assistant_message)
                    break

