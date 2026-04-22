"""
Command parsing and dispatch system for crafterscode agents.

This module provides a command system that allows users to execute
special commands starting with '/' across different channels.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple
from enum import Enum
import importlib
import inspect

from app.channel import Channel
from app.config import get


class CommandCategory(str, Enum):
    """Categories for organizing commands."""
    SYSTEM = "system"
    TOOLS = "tools"
    AGENT = "agent"
    CONFIG = "config"
    CHANNEL = "channel"
    UTILITY = "utility"


class Command:
    """Represents a command that can be executed."""
    
    def __init__(
        self,
        name: str,
        handler: Callable,
        description: str,
        usage: str,
        aliases: List[str] = None,
        category: CommandCategory = CommandCategory.UTILITY,
        channels: List[Channel] = None,
        requires_permission: bool = False,
    ):
        self.name = name
        self.handler = handler
        self.description = description
        self.usage = usage
        self.aliases = aliases or []
        self.category = category
        self.channels = channels or [Channel.CLI]
        self.requires_permission = requires_permission
    
    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)


class CommandRegistry:
    """Registry for managing all available commands."""
    
    def __init__(self):
        self._commands: Dict[str, Command] = {}
        self._aliases: Dict[str, str] = {}
    
    def register(self, command: Command) -> None:
        """Register a new command."""
        self._commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            self._aliases[alias] = command.name
    
    def find(self, name: str) -> Optional[Command]:
        """Find a command by name or alias."""
        # Check direct command name
        if name in self._commands:
            return self._commands[name]
        
        # Check aliases
        if name in self._aliases:
            actual_name = self._aliases[name]
            return self._commands.get(actual_name)
        
        return None
    
    def get_all(self) -> List[Command]:
        """Get all registered commands."""
        return list(self._commands.values())
    
    def get_by_category(self, category: CommandCategory) -> List[Command]:
        """Get commands by category."""
        return [cmd for cmd in self._commands.values() if cmd.category == category]
    
    def get_for_channel(self, channel: Channel) -> List[Command]:
        """Get commands available for a specific channel."""
        return [cmd for cmd in self._commands.values() if channel in cmd.channels]


class CommandParser:
    """Parses command strings and extracts arguments."""
    
    @staticmethod
    def parse(input_str: str) -> Tuple[str, List[str], Dict[str, str]]:
        """
        Parse a command string.
        
        Returns:
            Tuple of (command_name, positional_args, keyword_args)
        
        Example:
            "/model show --verbose" -> ("model", ["show"], {"verbose": ""})
            "/help tools --detail true" -> ("help", ["tools"], {"detail": "true"})
        """
        if not input_str.startswith("/"):
            raise ValueError("Command must start with '/'")
        
        # Remove leading slash
        input_str = input_str[1:].strip()
        
        if not input_str:
            return "", [], {}
        
        parts = []
        in_quotes = False
        current_part = ""
        
        # Tokenize with quote handling
        for char in input_str:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
                current_part += char
            elif char == " " and not in_quotes:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
        
        if current_part:
            parts.append(current_part)
        
        if not parts:
            return "", [], {}
        
        command_name = parts[0]
        positional = []
        keyword = {}
        
        i = 1
        while i < len(parts):
            arg = parts[i]
            
            if arg.startswith("--"):
                # Keyword argument
                key = arg[2:]
                if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                    # Has a value
                    value = parts[i + 1]
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    keyword[key] = value
                    i += 2
                else:
                    # Boolean flag
                    keyword[key] = ""
                    i += 1
            else:
                # Positional argument
                positional.append(arg)
                i += 1
        
        return command_name, positional, keyword


class CommandDispatcher:
    """Dispatches commands to their handlers."""
    
    def __init__(self, registry: CommandRegistry):
        self.registry = registry
    
    async def dispatch(
        self,
        command_input: str,
        channel: Channel,
        user_identity: Optional[str] = None,
    ) -> str:
        """
        Dispatch a command to its handler.
        
        Args:
            command_input: The raw command string (including '/')
            channel: The channel the command came from
            user_identity: Optional user identity for permission checking
        
        Returns:
            The response from the command handler
        """
        try:
            # Parse command
            command_name, args, kwargs = CommandParser.parse(command_input)
            
            if not command_name:
                return "Error: No command specified"
            
            # Find command
            command = self.registry.find(command_name)
            if not command:
                return f"Error: Command '/{command_name}' not found. Use /help for available commands."
            
            # Check if command is available for this channel
            if channel not in command.channels:
                return f"Error: Command '/{command_name}' is not available in this channel."
            
            # Check permissions if required
            if command.requires_permission and not self._check_permission(user_identity):
                return "Error: You don't have permission to execute this command."
            
            # Execute command
            try:
                # Check if handler is async
                if inspect.iscoroutinefunction(command.handler):
                    result = await command.handler(args, kwargs, channel, user_identity)
                else:
                    result = command.handler(args, kwargs, channel, user_identity)
                return result
            except Exception as e:
                return f"Error executing command '/{command_name}': {str(e)}"
        
        except Exception as e:
            return f"Error parsing command: {str(e)}"
    
    def _check_permission(self, user_identity: Optional[str]) -> bool:
        """Check if user has permission to execute commands."""
        # Simple permission check - can be enhanced with proper auth system
        return True  # Allow all for now


# Built-in command implementations

async def handle_model(args: List[str], kwargs: Dict[str, str], channel: Channel, user_identity: Optional[str]) -> str:
    """
    Handle the /model command.
    
    Usage: /model [show|set] [--verbose]
    
    Examples:
        /model
        /model show
        /model show --verbose
    """
    action = args[0] if args else "show"
    verbose = "verbose" in kwargs
    
    model = get("model", "Not configured")
    base_url = get("base_url", "Not configured")
    max_tokens = get("max_tokens", "Not configured")
    max_iterations = get("max_iterations", "Not configured")
    
    if action == "show":
        if verbose:
            return (
                f"📊 Model Configuration 📊\n"
                f"├─ Model: {model}\n"
                f"├─ Base URL: {base_url}\n"
                f"├─ Max Tokens: {max_tokens}\n"
                f"└─ Max Iterations: {max_iterations}"
            )
        else:
            return f"🤖 Current model: {model}"
    
    elif action == "set":
        if len(args) < 2:
            return "Usage: /model set <model_name>"
        
        new_model = args[1]
        # Note: In a real implementation, this would update the config
        return f"⚠️ Model changing not implemented yet. Would change to: {new_model}"
    
    else:
        return f"Error: Unknown action '{action}'. Use 'show' or 'set'."


async def handle_help(args: List[str], kwargs: Dict[str, str], channel: Channel, user_identity: Optional[str]) -> str:
    """
    Handle the /help command.
    
    Usage: /help [command|category]
    
    Examples:
        /help
        /help model
        /help tools
    """
    if args:
        # Show help for specific command or category
        target = args[0]
        
        # Check if it's a category
        try:
            category = CommandCategory(target)
            commands = _registry.get_by_category(category)
            if commands:
                lines = [f"📚 Commands in category '{category}':"]
                for cmd in commands:
                    if channel in cmd.channels:
                        lines.append(f"  /{cmd.name} - {cmd.description}")
                return "\n".join(lines)
        except ValueError:
            # Not a category, check if it's a command
            pass
        
        # Check if it's a command
        command = _registry.find(target)
        if command:
            if channel not in command.channels:
                return f"❌ Command '/{target}' is not available in this channel."
            
            response = [
                f"📋 Command: /{command.name}",
                f"📝 Description: {command.description}",
                f"📖 Usage: {command.usage}",
            ]
            
            if command.aliases:
                response.append(f"🔤 Aliases: {', '.join(f'/{alias}' for alias in command.aliases)}")
            
            if command.category:
                response.append(f"📂 Category: {command.category}")
            
            return "\n".join(response)
        
        # Check if it's a channel name
        try:
            channel_enum = Channel(target)
            commands = _registry.get_for_channel(channel_enum)
            if commands:
                lines = [f"📱 Commands available in channel '{channel_enum}':"]
                for cmd in commands:
                    lines.append(f"  /{cmd.name} - {cmd.description}")
                return "\n\n".join(lines)
        except ValueError:
            pass
        
        return f"❌ No command, category, or channel named '{target}' found."
    
    # Show general help
    lines = [
        "📚 Available Commands 📚",
        "",
        "Type /help <command> for detailed help on a specific command.",
        "Type /help <category> to see commands in a category.",
        "",
        "📂 Categories:"
    ]
    
    # List categories
    for category in CommandCategory:
        commands = _registry.get_by_category(category)
        if any(channel in cmd.channels for cmd in commands):
            channel_commands = [cmd for cmd in commands if channel in cmd.channels]
            if channel_commands:
                lines.append(f"  {category.value}: {len(channel_commands)} commands")
    
    lines.extend([
        "",
        "🔧 System Commands:",
        "  /help - Show this help message",
        "  /model - Show or change the current model",
        "  /config - Show or update configuration",
        "",
        "💡 Tip: Commands start with '/' and support arguments and flags (--flag value)."
    ])
    
    return "\n".join(lines)


async def handle_config(args: List[str], kwargs: Dict[str, str], channel: Channel, user_identity: Optional[str]) -> str:
    """
    Handle the /config command.
    
    Usage: /config [show|get|set] [key] [value] [--verbose]
    
    Examples:
        /config
        /config show
        /config get model
        /config set model "anthropic/claude-3.5-sonnet"
    """
    action = args[0] if args else "show"
    verbose = "verbose" in kwargs
    
    # Get config directly
    model = get("model", "Not configured")
    base_url = get("base_url", "Not configured")
    max_tokens = get("max_tokens", "Not configured")
    max_iterations = get("max_iterations", "Not configured")
    
    config_dict = {
        "model": model,
        "base_url": base_url,
        "max_tokens": max_tokens,
        "max_iterations": max_iterations,
    }
    
    if action == "show":
        lines = ["🔧 Configuration:"]
        for key, value in config_dict.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    
    elif action == "get":
        if len(args) < 2:
            return "Usage: /config get <key>"
        
        key = args[1]
        if key in config_dict:
            return f"{key}: {config_dict[key]}"
        else:
            return f"❌ Configuration key '{key}' not found."
    
    elif action == "set":
        if len(args) < 3:
            return "Usage: /config set <key> <value>"
        
        key = args[1]
        value = args[2]
        # Note: In a real implementation, this would update the config
        return f"⚠️ Configuration updating not implemented yet. Would set {key} = {value}"
    
    else:
        return f"❌ Unknown action '{action}'. Use 'show', 'get', or 'set'."


async def handle_tools(args: List[str], kwargs: Dict[str, str], channel: Channel, user_identity: Optional[str]) -> str:
    """
    Handle the /tools command.
    
    Usage: /tools [list|info] [tool_name]
    
    Examples:
        /tools
        /tools list
        /tools info bash
    """
    from app.tool_calls import tool_registry
    
    action = args[0] if args else "list"
    
    if action == "list":
        tools = list(tool_registry.keys())
        lines = ["🛠️ Available Tools:"]
        for tool_name in sorted(tools):
            tool_info = tool_registry[tool_name]
            description = tool_info["spec"]["function"]["description"][:50] + "..."
            lines.append(f"  {tool_name}: {description}")
        return "\n".join(lines)
    
    elif action == "info":
        if len(args) < 2:
            return "Usage: /tools info <tool_name>"
        
        tool_name = args[1]
        if tool_name not in tool_registry:
            return f"❌ Tool '{tool_name}' not found."
        
        tool_info = tool_registry[tool_name]["spec"]
        func = tool_info["function"]
        
        lines = [
            f"🛠️ Tool: {func['name']}",
            f"📝 Description: {func['description']}",
        ]
        
        if "parameters" in func:
            params = func["parameters"]["properties"]
            if params:
                lines.append("📋 Parameters:")
                for param_name, param_spec in params.items():
                    required = param_name in func["parameters"].get("required", [])
                    req_mark = " (required)" if required else ""
                    param_type = param_spec.get("type", "any")
                    lines.append(f"  {param_name}: {param_spec.get('description', 'No description')} [{param_type}]{req_mark}")
        
        return "\n".join(lines)
    
    else:
        return f"❌ Unknown action '{action}'. Use 'list' or 'info'."


async def handle_skills(args: List[str], kwargs: Dict[str, str], channel: Channel, user_identity: Optional[str]) -> str:
    """
    Handle the /skills command.
    
    Usage: /skills [list|info] [skill_name]
    
    Examples:
        /skills
        /skills list
        /skills info puppeteer
    """
    import os
    
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    
    if not os.path.exists(skills_dir):
        return "❌ Skills directory not found."
    
    skills = []
    for item in os.listdir(skills_dir):
        skill_dir = os.path.join(skills_dir, item)
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if os.path.isdir(skill_dir) and os.path.exists(skill_md):
            skills.append(item)
    
    action = args[0] if args else "list"
    
    if action == "list":
        if not skills:
            return "❌ No skills available."
        
        lines = ["🧠 Available Skills:"]
        for skill in sorted(skills):
            lines.append(f"  {skill}")
        return "\n".join(lines)
    
    elif action == "info":
        if len(args) < 2:
            return "Usage: /skills info <skill_name>"
        
        skill_name = args[1]
        skill_md = os.path.join(skills_dir, skill_name, "SKILL.md")
        
        if not os.path.exists(skill_md):
            return f"❌ Skill '{skill_name}' not found."
        
        try:
            with open(skill_md, "r") as f:
                content = f.read()
            
            # Extract first few lines for summary
            lines = content.strip().split("\n")[:10]
            summary = "\n".join(lines)
            
            return (
                f"🧠 Skill: {skill_name}\n"
                f"📄 Summary:\n{summary}\n"
                f"\n📝 Full documentation available in: {skill_md}"
            )
        except Exception as e:
            return f"❌ Error reading skill: {str(e)}"
    
    else:
        return f"❌ Unknown action '{action}'. Use 'list' or 'info'."


async def handle_quit(args: List[str], kwargs: Dict[str, str], channel: Channel, user_identity: Optional[str]) -> str:
    """
    Handle the /quit command.
    
    Usage: /quit [--force]
    
    Example:
        /quit
        /quit --force
    """
    force = "force" in kwargs
    
    if channel == Channel.CLI:
        return "👋 Goodbye! Use Ctrl+C to exit."
    else:
        return "👋 Goodbye!"


# Initialize the registry
_registry = CommandRegistry()

# Register built-in commands
_registry.register(Command(
    name="help",
    handler=handle_help,
    description="Show help for commands",
    usage="/help [command|category]",
    aliases=["h", "?"],
    category=CommandCategory.SYSTEM,
    channels=list(Channel),  # Available in all channels
))

_registry.register(Command(
    name="model",
    handler=handle_model,
    description="Show or change the current AI model",
    usage="/model [show|set] [--verbose]",
    category=CommandCategory.SYSTEM,
    channels=list(Channel),
))

_registry.register(Command(
    name="config",
    handler=handle_config,
    description="Show or update configuration",
    usage="/config [show|get|set] [key] [value] [--verbose]",
    category=CommandCategory.CONFIG,
    channels=list(Channel),
))

_registry.register(Command(
    name="tools",
    handler=handle_tools,
    description="List available tools or show tool details",
    usage="/tools [list|info] [tool_name]",
    aliases=["tool"],
    category=CommandCategory.TOOLS,
    channels=list(Channel),
))

_registry.register(Command(
    name="skills",
    handler=handle_skills,
    description="List available skills or show skill details",
    usage="/skills [list|info] [skill_name]",
    aliases=["skill"],
    category=CommandCategory.TOOLS,
    channels=list(Channel),
))

_registry.register(Command(
    name="quit",
    handler=handle_quit,
    description="Quit the agent",
    usage="/quit [--force]",
    aliases=["exit", "q"],
    category=CommandCategory.SYSTEM,
    channels=[Channel.CLI],  # Only in CLI for now
))

# Create dispatcher
dispatcher = CommandDispatcher(_registry)


# Utility functions for external use
def get_dispatcher() -> CommandDispatcher:
    """Get the command dispatcher instance."""
    return dispatcher

def get_registry() -> CommandRegistry:
    """Get the command registry instance."""
    return _registry

def is_command(input_str: str) -> bool:
    """Check if input string is a command."""
    return input_str.strip().startswith("/") if input_str else False

async def handle_command(input_str: str, channel: Channel = Channel.CLI, user_identity: Optional[str] = None) -> str:
    """
    Handle a command input.
    
    This is the main entry point for command processing.
    """
    return await dispatcher.dispatch(input_str, channel, user_identity)