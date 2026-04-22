from __future__ import annotations

import json
import asyncio

import app.config as config
from app.client import Client
from app.tool_calls import run_tool, tool_registry
from app.helpers import load_system_context
from app.display import log
from app.channel import Channel
from app.message import OutgoingMessage, IncomingMessage
from app.message_queue import MessageQueue
from app.cli import ask_permission
from app.commands import is_command, handle_command


class Agent:

    def __init__(self, mq: MessageQueue = None, channel: Channel = Channel.CLI, max_iterations: int = 100, auto_approve: bool = False, silent: bool = False) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
        self.auto_approve = auto_approve
        self.max_iterations = max_iterations
        self.silent = silent
        self.mq = mq
        self.channel = channel

        system_context = load_system_context()
        if system_context:
            self.messages.append({"role": "system", "content": system_context})

    async def process_incoming(self) -> None:
        while True:
            msg = await self.mq.incoming.get()
            await self.process_message(msg.content)

    async def process_message(self, message: str) -> None:
        """Process a message - check if it's a command or regular message."""
        # Check if this is a command
        if is_command(message):
            log.info(f"Processing command: {message[:50]}...")
            try:
                # Handle command
                response = await handle_command(message, self.channel)
                
                # Send command response back to user
                if self.mq:
                    await self.mq.outgoing_msg(OutgoingMessage(content=response, channel=self.channel))
                
                return  # Command handled, don't process as normal message
            
            except Exception as e:
                error_msg = f"Error processing command: {str(e)}"
                log.error(error_msg)
                if self.mq:
                    await self.mq.outgoing_msg(OutgoingMessage(content=error_msg, channel=self.channel))
                return
        
        # Not a command, process as normal agent message
        await self.agent_loop(message)

    async def agent_loop(self, message: str) -> None:
        
        self.messages.append({"role": "user", "content": message})
        tool_specs = [tool["spec"] for tool in tool_registry.values()]

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            log.info("chat.completions.create...")
            chat = await self.client.chat.completions.create(
                model=config.get("model", "deepseek/deepseek-v3.2"),
                messages=self.messages,
                tools=tool_specs,
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

            self.messages.append(assistant_message)

            if assistant_message.tool_calls is not None:
    
                if not self.silent and assistant_message.content is not None and assistant_message.content.strip() != "":
                    #print(assistant_message.content.strip())
                    if self.mq:
                        await self.mq.outgoing_msg(OutgoingMessage(content=assistant_message.content.strip(), channel=self.channel))

                for tool_call in assistant_message.tool_calls:

                    try:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        result = ""

                        if not self.auto_approve and self.channel == Channel.CLI:
                            if not await ask_permission(self.mq, tool_name, tool_args):
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
                if assistant_message.content.strip() != "":
                    #print(assistant_message.content)
                    if self.mq:
                        await self.mq.outgoing_msg(OutgoingMessage(content=assistant_message.content.strip(), channel=self.channel))

                if finish_reason in ("stop", None):
                    break