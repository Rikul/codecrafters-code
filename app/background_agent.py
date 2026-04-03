from __future__ import annotations

import json

import app.config as config
from app.client import Client
from app.tool_calls import run_tool, tool_registry
from app.helpers import load_system_context
from app.display import log
from app.channel import Channel
from app.message import OutgoingMessage
from app.message_queue import MessageQueue

class BackgroundAgent:

    def __init__(self, mq: MessageQueue = None, channel: Channel = None, max_iterations: int = 100) -> None:
        self.client = Client().get_client()
        self.messages: list[dict] = []
        self.max_iterations = max_iterations
        self.mq = mq
        self.channel = channel

        if self.channel is None:
            ValueError("channel must be specified for BackgroundAgent")

        system_context = load_system_context()
        if system_context:
            self.messages.append({"role": "system", "content": system_context})

    async def process_incoming(self) -> None:
        log.info("BackgroundAgent started processing incoming messages...")
        while True:
            msg = await self.mq.incoming.get()
            await self.agent_loop(msg.content, msg.metadata)

    async def agent_loop(self, message: str, metadata: dict = None) -> None:
        self._reply_metadata = metadata or {}
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
                response_format={"type": "text"},
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
    
                if assistant_message.content is not None and assistant_message.content.strip() != "":
                    if self.mq:
                        await self.mq.outgoing_msg(OutgoingMessage(content=assistant_message.content.strip(), channel=self.channel, metadata=self._reply_metadata))

                for tool_call in assistant_message.tool_calls:

                    try:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
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
                    if self.mq:
                        await self.mq.outgoing_msg(OutgoingMessage(content=assistant_message.content.strip(), channel=self.channel, metadata=self._reply_metadata))

                if finish_reason in ("stop", None):
                    break

