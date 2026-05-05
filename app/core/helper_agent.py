from __future__ import annotations

import json

from .. import config
from ..infra.app_logging import log
from .agent import Agent


class HelperAgent(Agent):

    def __init__(self, system_prompt: str = None, max_iterations: int = 50) -> None:
        super().__init__(max_iterations)
        if system_prompt:
            if self.messages and self.messages[0]["role"] == "system":
                self.messages[0]["content"] = system_prompt
            else:
                self.messages.insert(0, {"role": "system", "content": system_prompt})

    async def run(self, prompt: str) -> str:
        log.info(f"Running HelperAgent with prompt: {prompt}")
        return await self.agent_loop(prompt)

    async def agent_loop(self, message: str, metadata: dict = None) -> str:
        from .tool_calls import helper_tool_specs, run_tool
        self.messages.append({"role": "user", "content": message})
        iteration = 0
        assistant_message = None

        while iteration < self.max_iterations:
            iteration += 1

            log.info(f"HelperAgent iteration {iteration}")
            chat = await self.client.chat.completions.create(
                model=config.get("model", "deepseek/deepseek-v3.2"),
                messages=self.messages,
                tools=helper_tool_specs
            )

            if not chat.choices:
                raise RuntimeError("No choices in API response")

            choice = chat.choices[0]
            assistant_message = choice.message
            finish_reason = getattr(choice, "finish_reason", None)
            if not isinstance(finish_reason, str):
                finish_reason = None

            if assistant_message.tool_calls is not None:
                self.messages.append(self._serialize_assistant_msg(assistant_message))

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

            else:
                if finish_reason == "stop":
                    break

        return assistant_message.content.strip() if assistant_message and assistant_message.content else ""
