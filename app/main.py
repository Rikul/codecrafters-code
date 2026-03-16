import os
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from app.display import log
from app.agent import Agent

async def input_loop(session: PromptSession):
    while True:
        try:
            with patch_stdout():
                user_input = await session.prompt_async("› ")
            yield user_input
        except (EOFError, KeyboardInterrupt):
            print("Exiting...")
            break

async def main():

    p = argparse.ArgumentParser()
    p.add_argument("-p", "--prompt", metavar="PROMPT", dest="prompt", type=str, required=True, 
                   help="The initial prompt for the agent")
    p.add_argument("--auto-approve", dest="auto_approve", action="store_true", 
                   help="Allow the agent to call tools without asking for permission")
    p.add_argument("--no-repl", dest="no_repl", action="store_true", 
                   help="Run the agent with the initial prompt and then exit without starting the REPL")
    p.add_argument("--workspace", metavar="path", dest="workspace", type=str, 
                   help="The directory where the agent will work (default: current directory)")
    p.add_argument("--max-iterations", metavar="N", dest="max_iterations", type=int, default=100,
                   help="The maximum number of iterations the agent will run before stopping (default: 100)")
    
    args = p.parse_args()
    
    # validate workspace
    if args.workspace:
        if os.path.exists(args.workspace) and not os.path.isdir(args.workspace):
            print(f"Workspace path {args.workspace} is not a directory")
            return
        
        if not os.path.exists(args.workspace):
            try:
                os.makedirs(args.workspace)
            except Exception as e:
                print(f"Error creating workspace directory {args.workspace}: {e}")
                return

    # validate max_iterations
    if args.max_iterations <= 0:
        print("max_iterations must be a positive integer")
        return
    
    session = PromptSession()
    agent = Agent(auto_approve=args.auto_approve, workspace=args.workspace, max_iterations=args.max_iterations)

    log.info("Starting agent...")
    await agent.agent_loop(args.prompt)
    
    if args.no_repl:
        return
    
    async for user_input in input_loop(session):
        await agent.agent_loop(user_input)
        
    
if __name__ == "__main__":
    asyncio.run(main())
