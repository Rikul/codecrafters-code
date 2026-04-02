from app.channel import Channel
from app.message_queue import MessageQueue
from app.message import IncomingMessage, OutgoingMessage
import asyncio, app.display as display

async def ask_permission(mq: MessageQueue, tool_name: str, args: dict) -> bool:
    msg = f"{display.YELLOW}⚡ Tool Call{display.RESET}: {display.CYAN}{tool_name}{display.RESET}   Args: {args}"
    await mq.outgoing_msg(OutgoingMessage(content=msg, channel=Channel.CLI))

    msg = f"Proceed? {display.DIM}[Y/n]{display.RESET} "
    await mq.outgoing_msg(OutgoingMessage(content=msg, channel=Channel.CLI))
    
    result = await mq.incoming.get()
    answer = result.content.strip().lower()
    return answer in ("", "y", "yes")

class CLI:
    def __init__(self, queue: MessageQueue, loop: asyncio.AbstractEventLoop):
        self.queue = queue
        self.loop = loop
        queue.register(Channel.CLI, self.deliver)

    async def deliver(self, msg: OutgoingMessage):
        print(f"\n{display.GREEN}Agent:{display.RESET} {msg.content}\n")

    async def start(self):
        while True:
            user_input = await self.loop.run_in_executor(None, lambda: input("> "))
            print("", end="\r")  # clean up line

            if user_input.strip():
                msg = IncomingMessage(content=user_input, channel=Channel.CLI)
                await self.queue.incoming_msg(msg)