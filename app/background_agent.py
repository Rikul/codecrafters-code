from __future__ import annotations

import asyncio
import json

from . import config
from .tool_calls import run_tool, all_tool_specs
from .app_logging import log
from .channel import Channel, ChannelType
from .message import OutgoingMessage
from .message_queue import MessageQueue
from .agent import Agent, MAX_CONTEXT_MESSAGES

from .message_history import MessageHistory

class BackgroundAgent(Agent):

    def __init__(self, mq: MessageQueue = None, channel: Channel = None, max_iterations: int = 250) -> None:
        super().__init__(max_iterations)
        self.mq = mq
        self.channel = channel

        if self.channel is None:
            raise ValueError("channel must be specified for BackgroundAgent")

        self.history = MessageHistory(channel_type=channel.channel_type.value)
        self.messages.extend(self.history.get_history(limit=MAX_CONTEXT_MESSAGES))

    async def process_incoming(self) -> None:
        log.info("BackgroundAgent started processing incoming messages...")
        while True:
            msg = await self.mq.incoming.get()
            try:
                await self.agent_loop(msg.content, msg.metadata)
            except Exception as e:
                log.error(f"Agent loop error: {e}")

    async def agent_loop(self, message: str, metadata: dict = None) -> None:
        self._trim_messages()
        self.history.add_message("user", message)

        session_messages = self.messages[:] + [{"role": "user", "content": message}]
        self._reply_metadata = metadata or {}
        iteration = 0
        empty_retries = 0
        assistant_message = None
        MAX_RETRIES = 5

        while iteration < self.max_iterations:
            iteration += 1

            log.info("chat.completions.create...")
            chat = await self.client.chat.completions.create(
                model=config.get("model", "deepseek/deepseek-v3.2"),
                messages=session_messages,
                tools=all_tool_specs
            )

            if not chat.choices or len(chat.choices) == 0:
                empty_retries += 1
                if empty_retries > MAX_RETRIES:
                    raise RuntimeError(f"No choices in API response after {MAX_RETRIES} retries")
                wait = min(2 ** empty_retries, 60)
                log.warning(f"No choices in API response, retrying in {wait}s (attempt {empty_retries}/{MAX_RETRIES})")
                await asyncio.sleep(wait)
                continue

            empty_retries = 0

            choice = chat.choices[0]
            assistant_message = choice.message
            finish_reason = getattr(choice, "finish_reason", None)
            if not isinstance(finish_reason, str):
                finish_reason = None

            if assistant_message.tool_calls is not None:
                session_messages.append(assistant_message)

                llm_text = assistant_message.content.strip().rstrip(":").strip() if assistant_message.content else ""

                for tool_call in assistant_message.tool_calls:
                    try:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        first_arg = str(next(iter(tool_args.values()), ""))[:50] if tool_args else ""
                        tool_status = f"running {tool_name} [{first_arg}]..."
                        status_msg = f"{llm_text}: {tool_status}" if llm_text else tool_status
                        llm_text = ""  # only prepend on first tool call
                        if self.mq:
                            await self.mq.outgoing_msg(OutgoingMessage(content=status_msg, channel=self.channel, metadata=self._reply_metadata))
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
                    if self.mq:
                        await self.mq.outgoing_msg(OutgoingMessage(content=assistant_message.content.strip(), channel=self.channel, metadata=self._reply_metadata))
                
                if finish_reason == "stop":
                    session_messages.append(assistant_message)
                    break
            
            if self.channel.has_stopped:
                log.info("Channel has been stopped, breaking out of agent loop.")
                break
        
        self.channel.clear_stopped()

        if len(session_messages) >= 2 and assistant_message is not None:
            self.messages.append({"role": "user", "content": message})
            self.messages.append(session_messages[-1])
            assistant_content = assistant_message.content.strip() if assistant_message.content else ""
            self.history.add_message("assistant", assistant_content)
