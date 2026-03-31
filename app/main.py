from __future__ import annotations

import argparse
import asyncio
import logging
import os

from dotenv import load_dotenv
load_dotenv()

import app.config as config
from app.display import log

async def load_config() -> None:
    try:
        config.load()
    except FileNotFoundError:
        log.error("Configuration file not found. Please create config.toml")
        return
    except Exception as e:
        log.error(f"Failed to load configuration: {e}")
        return

async def main():

    await load_config()

    p = argparse.ArgumentParser()

    p.add_argument("-p", "--prompt", metavar="PROMPT", dest="prompt", type=str, required=True, 
                   help="The initial prompt for the agent")
    p.add_argument("-y", "--auto-approve", dest="auto_approve", action="store_true", 
                   help="Allow the agent to call tools without asking for permission")
    p.add_argument("-x", "--no-repl", dest="no_repl", action="store_true", 
                   help="Run the agent with the initial prompt and then exit without starting the REPL")
    p.add_argument("-i", "--max-iterations", metavar="N", dest="max_iterations", type=int, 
                   help="The maximum number of iterations the agent will run before stopping (default: 100)")
    p.add_argument("-s", "--silent", dest="silent", action="store_true",
                   help="Suppress all output except the final response (implies --auto-approve --no-repl)")

    args = p.parse_args()
    
    # validate max_iterations
    if args.max_iterations is None:
        args.max_iterations = config.get("max_iterations", 100)
        
    if args.max_iterations <= 0:
        log.error("max_iterations must be a positive integer")
        return

    if args.silent:
        log.setLevel(logging.WARNING)

    log.info("Starting agent...")

    from app.agent import Agent
    agent = Agent(auto_approve=args.auto_approve or args.silent, 
                  max_iterations=args.max_iterations, silent=args.silent)

    await agent.agent_loop(args.prompt)
    if args.no_repl or args.silent:
        return

    from app.input import input_loop

    try:

        async for user_input in input_loop():
            await agent.agent_loop(user_input)

    except KeyboardInterrupt:
        log.info("Exiting...")
        os._exit(0)

    except Exception as e:
        log.error(f"An error occurred: {e}")
    
if __name__ == "__main__":
    asyncio.run(main())
