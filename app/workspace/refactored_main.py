"""Main entry point for the agent application."""

import argparse
import logging
from typing import Optional

from app.agent import Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments.
        
    Raises:
        SystemExit: If required arguments are missing or invalid.
    """
    parser = argparse.ArgumentParser(
        description="Agent application runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--prompt",
        required=True,
        type=str,
        help="Initial prompt or path for the agent",
    )
    return parser.parse_args()


def run_agent(prompt: str) -> None:
    """Initialize and run the agent with the given prompt.
    
    Args:
        prompt: The initial prompt or path for the agent to process.
        
    Raises:
        Exception: If agent initialization or execution fails.
    """
    try:
        logger.info(f"Initializing agent with prompt: {prompt}")
        agent = Agent()
        agent.start_loop(prompt)
    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise


def main() -> None:
    """Main entry point for the application."""
    try:
        args = parse_arguments()
        run_agent(args.prompt)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
