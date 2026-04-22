"""
crafterscode - AI agent with tool calling capabilities
"""

__version__ = "0.1.0"

from .agent import Agent
from .channel import Channel
from .message import IncomingMessage, OutgoingMessage
from .message_queue import MessageQueue
from .client import Client
from .config import load, get
from .tool_calls import run_tool, tool_registry
from .commands import (
    Command,
    CommandRegistry,
    CommandParser,
    CommandDispatcher,
    get_dispatcher,
    get_registry,
    is_command,
    handle_command,
)

__all__ = [
    "Agent",
    "Channel",
    "IncomingMessage",
    "OutgoingMessage",
    "MessageQueue",
    "Client",
    "load",
    "get",
    "run_tool",
    "tool_registry",
    "Command",
    "CommandRegistry",
    "CommandParser",
    "CommandDispatcher",
    "get_dispatcher",
    "get_registry",
    "is_command",
    "handle_command",
]