from __future__ import annotations

import argparse
import asyncio
import logging
import os


from dotenv import load_dotenv
load_dotenv()

from app.message_queue import MessageQueue
from app.cli import CLI

import app.config as config
from app.display import log
from app.setup import ensure_home_dir

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
    
    ensure_home_dir()
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

    mq = MessageQueue()
    loop = asyncio.get_event_loop()
    cli = CLI(mq, loop)

    from app.agent import Agent
    agent = Agent(mq = mq, auto_approve=args.auto_approve or args.silent, 
                  max_iterations=args.max_iterations, silent=args.silent)

    # Send initial prompt to agent via message queue
    from app.message import IncomingMessage
    from app.channel import Channel
    await mq.incoming_msg(IncomingMessage(content=args.prompt, channel=Channel.CLI))

    if args.no_repl or args.silent:
        # For silent/no-repl mode, just run agent processing
        await agent.process_incoming()
        return

    try:
        await asyncio.gather(
            cli.start(),
            mq.process_outgoing(),
            agent.process_incoming(),
        )
    except KeyboardInterrupt:
        log.info("Exiting...")
        os._exit(0)
    
    except Exception as e:
        log.error(f"An error occurred: {e}")
    
if __name__ == "__main__":
    
    # For better Ctrl+C handling, we use asyncio.Runner which is available in Python 3.11 and later
    with asyncio.Runner() as runner:
        runner.run(main())