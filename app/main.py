import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio

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
    p.add_argument("-p", dest="prompt", type=str, required=True, help="The initial prompt to start the agent with")
    p.add_argument("--auto-approve", dest="auto_approve", action="store_true", 
                   help="Allow the agent to call tools without asking for permission")
    args = p.parse_args()

    session = PromptSession()
    agent = Agent(auto_approve=args.auto_approve)

    await agent.agent_loop(args.prompt)
    async for user_input in input_loop(session):
        await agent.agent_loop(user_input)
        
    
if __name__ == "__main__":
    asyncio.run(main())
