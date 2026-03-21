import os
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio
import logging

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

import app.config as config
from app.display import log
from app.agent import Agent

async def input_loop(session: PromptSession):
    while True:
        try:
            with patch_stdout():
                user_input = await session.prompt_async("› ")
            yield user_input
        except (EOFError, KeyboardInterrupt):
            log.info("Exiting...")
            break

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
    
    p.add_argument("--auto-approve", dest="auto_approve", action="store_true", 
                   help="Allow the agent to call tools without asking for permission")
    
    p.add_argument("--no-repl", dest="no_repl", action="store_true", 
                   help="Run the agent with the initial prompt and then exit without starting the REPL")
    
    p.add_argument("--max-iterations", metavar="N", dest="max_iterations", type=int, 
                   help="The maximum number of iterations the agent will run before stopping (default: 100)")
    
    p.add_argument("--silent", dest="silent", action="store_true",
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

    session = PromptSession()
    agent = Agent(auto_approve=args.auto_approve or args.silent, 
                  max_iterations=args.max_iterations, silent=args.silent)

    log.info("Starting agent...")
    await agent.agent_loop(args.prompt)
    
    if args.no_repl or args.silent:
        return
    
    async for user_input in input_loop(session):
        await agent.agent_loop(user_input)
        
    
if __name__ == "__main__":
    asyncio.run(main())
