import argparse

from app.agent import Agent

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", dest="prompt", type=str, required=True, help="The initial prompt to start the agent with")
    p.add_argument("--auto-approve", dest="auto_approve", action="store_true", 
                   help="Allow the agent to call tools without asking for permission")
    args = p.parse_args()

    agent = Agent()
    agent.start_loop(args.prompt, auto_approve=args.auto_approve)

if __name__ == "__main__":
    main()
