import argparse
import os
import sys

from app.agent import Agent

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    agent = Agent()
    agent.start_loop(args.p)

if __name__ == "__main__":
    main()
