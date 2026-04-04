from .display import ANSI
import asyncio

def ask_permission(tool_name: str, args: dict) -> bool:
    msg = f"{ANSI.YELLOW}⚡ Tool Call{ANSI.RESET}: {ANSI.CYAN}{tool_name}{ANSI.RESET}   Args: {args}"
    print(msg)

    msg = f"Proceed? {ANSI.DIM}[Y/n]{ANSI.RESET} "
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