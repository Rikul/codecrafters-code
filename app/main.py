from __future__ import annotations

import argparse
import asyncio
import logging
import os

from dotenv import load_dotenv
load_dotenv()

from . import config
from .display import log
from .setup import ensure_home_dir
from .cli import input_loop
from .cli_agent import CliAgent
from .server import start_server

async def load_config() -> None:
    try:
        config.load()
    except FileNotFoundError:
        log.error("Configuration file not found. Please create config.toml")
        return
    except Exception as e:
        log.error(f"Failed to load configuration: {e}")
        return

def parse_args():
    parser = argparse.ArgumentParser(prog="app")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cli_parser = subparsers.add_parser("cli", help="Run interactive CLI")

    cli_parser.add_argument("-p", "--prompt", metavar="PROMPT", dest="prompt", type=str, required=True, 
                   help="The initial prompt for the agent")
    cli_parser.add_argument("-y", "--auto-approve", dest="auto_approve", action="store_true", 
                   help="Allow the agent to call tools without asking for permission")
    cli_parser.add_argument("-x", "--no-repl", dest="no_repl", action="store_true", 
                   help="Run the agent with the initial prompt and then exit without starting the REPL")
    cli_parser.add_argument("-i", "--max-iterations", metavar="N", dest="max_iterations", type=int, 
                   help="The maximum number of iterations the agent will run before stopping (default: 100)")
    cli_parser.add_argument("-s", "--silent", dest="silent", action="store_true",
                   help="Suppress all output except the final response (implies --auto-approve --no-repl)")

    bg_parser = subparsers.add_parser("background", help="Run in background")
    #bg_parser.add_argument("-c", "--channel", metavar="CHANNEL", dest="channel", type=str, required=True)

    return parser.parse_args()
    
async def run_cli(args):

    # validate max_iterations
    if args.max_iterations is None:
        args.max_iterations = config.get("max_iterations", 100)
        
    if args.max_iterations <= 0:
        log.error("max_iterations must be a positive integer")
        return

    if args.silent:
        log.setLevel(logging.WARNING)

    log.info("Starting agent...")
    agent = CliAgent(auto_approve=args.auto_approve or args.silent, max_iterations=args.max_iterations, silent=args.silent)

    await agent.agent_loop(args.prompt)
    if args.no_repl or args.silent:
        return

    try:
        async for user_input in input_loop():
            await agent.agent_loop(user_input)
    except KeyboardInterrupt:
        log.info("Exiting...")
        os._exit(0)
    except Exception as e:
        log.error(f"An error occurred: {e}")


async def run_background_agent(args):

    from .server import start_server
    await start_server()


async def main():
    
    ensure_home_dir()
    await load_config()

    args = parse_args()

    if args.command == "cli":
        await run_cli(args)
    elif args.command == "background":
        await run_background_agent(args)
    else:
        raise ValueError(f"Unknown command: {args.command}")
    
    
if __name__ == "__main__":
    
    # For better Ctrl+C handling, we use asyncio.Runner which is available in Python 3.11 and later
    with asyncio.Runner() as runner:
        runner.run(main())
        