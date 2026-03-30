from __future__ import annotations

import asyncio
import sys

async def input_loop() -> str:
    loop = asyncio.get_event_loop()
    
    while True:
        try:

            user_input = await loop.run_in_executor(None, lambda: input("> "))
            print("", end="\r")  # clean up line

            if user_input.strip():
                yield user_input

        except asyncio.CancelledError:
            raise KeyboardInterrupt
        
        