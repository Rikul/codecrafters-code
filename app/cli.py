from app.channel import Channel
from app.message_queue import MessageQueue
from app.message import IncomingMessage, OutgoingMessage
import app.display as display
import asyncio

def ask_permission(tool_name: str, args: dict) -> bool:
    msg = f"{display.YELLOW}⚡ Tool Call{display.RESET}: {display.CYAN}{tool_name}{display.RESET}   Args: {args}"
    print(msg)

    msg = f"Proceed? {display.DIM}[Y/n]{display.RESET} "
    print(msg, end="", flush=True)

    answer = input().strip().lower()
    return answer in ("", "y", "yes")

async def input_loop() -> str:
    loop = asyncio.get_event_loop()
    
    while True:
        try:
            user_input = await loop.run_in_executor(None, lambda: input("> "))
            print("", end="\r")  # clean up line

            if user_input.strip():
                yield user_input

        except (EOFError, KeyboardInterrupt):
            # Stop the loop on EOF or Ctrl+C
            break
        except asyncio.CancelledError:
            raise KeyboardInterrupt