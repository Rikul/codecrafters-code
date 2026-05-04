from __future__ import annotations

import json

from . import config
from .tool_calls import run_tool, all_tool_specs
from .app_logging import log
from .cli import ask_permission
from .agent import Agent, MAX_CONTEXT_MESSAGES
from .message_history import MessageHistory
from .channel import ChannelType

class CliAgent(Agent):

    def __init__(self, max_iterations: int = 250, auto_approve: bool = False, silent: bool = False) -> None:
        super().__init__(max_iterations)
        self.auto_approve = auto_approve or silent
        self.silent = silent
        self.history = MessageHistory(channel_type=ChannelType.CLI.value)
        self.messages.extend(self.history.get_history(limit=MAX_CONTEXT_MESSAGES))

    async def agent_loop(self, message: str,  metadata: dict = None) -> None:
        self._trim_messages()
        self.history.add_message("user", message)

        session_messages = self.messages[:] + [{"role": "user", "content": message}]
        iteration = 0
        assistant_message = ""
        while iteration < self.max_iterations:
            iteration += 1

            log.info("chat.completions.create...")
            chat = await self.client.chat.completions.create(
                model=config.get("model", "deepseek/deepseek-v3.2"),
                messages=session_messages,
                tools=all_tool_specs
            )

            if not chat.choices or len(chat.choices) == 0:
                raise RuntimeError("no choices in response")

            choice = chat.choices[0]
            assistant_message = choice.message
            finish_reason = getattr(choice, "finish_reason", None)
            if not isinstance(finish_reason, str):
                finish_reason = None

            if assistant_message.tool_calls is not None:
                session_messages.append(self._serialize_assistant_msg(assistant_message))

                if not self.silent and assistant_message.content is not None and assistant_message.content.strip() != "":
                    print(assistant_message.content.strip())
                    
                for tool_call in assistant_message.tool_calls:

                    try:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        result = ""

                        if not self.auto_approve and not ask_permission(tool_name, tool_args):
                            session_messages.append({
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

                    session_messages.append({
                            "role": "tool", 
                            "tool_call_id": tool_call.id, 
                            "name": tool_name, 
                            "content": result
                    })

                    log.info(f"{result[:250]}...")

            else:
                if assistant_message.content is not None and assistant_message.content.strip() != "":
                    print(assistant_message.content)

                if finish_reason == "stop":
                    session_messages.append(self._serialize_assistant_msg(assistant_message))
                    break
        
        if len(session_messages) >= 2:  # only add to history if there's something beyond the initial user message and assistant response
            self.messages.append({"role": "user", "content": message})
            self.messages.append(session_messages[-1]) 
            self.history.add_message("assistant", assistant_message.content.strip() if assistant_message.content else "")