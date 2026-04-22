# Agents System - crafterscode

## Overview

The crafterscode agents system is a modular, extensible framework for building AI agents with tool-calling capabilities. This document describes the architecture, components, and extensibility patterns for the system.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────┐
│               Message Queue                 │
│  (app/message_queue.py)                     │
│  • Asynchronous message routing             │
│  • Channel-based delivery                   │
│  • Thread-safe operations                   │
└───────────────┬─────────────────────────────┘
                │
      ┌─────────┴─────────┐
      ▼                   ▼
┌─────────────┐   ┌─────────────┐
│   Channel   │   │   Agent     │
│   (app/channel.py)     (app/agent.py)      │
│  • CLI      │   │  • LLM orchestration     │
│  • Discord  │   │  • Tool calling          │
│  • WebSocket│   │  • Iteration control     │
│  • API      │   └─────────────┘
└─────────────┘
```

### Message Flow

1. **Incoming**: User input → Channel → Message Queue → Agent
2. **Outgoing**: Agent → Tool calls → Message Queue → Channel → User
3. **Tool Responses**: Tool execution → Message Queue → Agent → Response formatting → Channel

## Channel System

### Available Channels

| Channel | Description | Implementation |
|---------|-------------|----------------|
| **CLI** | Command-line interface | `app/cli.py` |
| **Discord** | Discord bot (planned) | (Future implementation) |
| **WebSocket** | Real-time web interface | (Future implementation) |
| **API** | REST/GraphQL endpoints | (Future implementation) |

### Creating New Channels

To add a new channel:

1. **Extend `Channel` enum** in `app/channel.py`:
   ```python
   from enum import Enum
   class Channel(str, Enum):
       CLI = "cli"
       DISCORD = "discord"
       WEBSOCKET = "websocket"
       API = "api"
       YOUR_CHANNEL = "your_channel"
   ```

2. **Create channel implementation**:
   ```python
   # app/channels/your_channel.py
   from app.channel import Channel
   from app.message_queue import MessageQueue
   from app.message import IncomingMessage, OutgoingMessage
   
   class YourChannel:
       def __init__(self, queue: MessageQueue, config: dict):
           self.queue = queue
           self.config = config
           queue.register(Channel.YOUR_CHANNEL, self.deliver)
       
       async def deliver(self, msg: OutgoingMessage):
           # Send message to your channel
           pass
       
       async def start(self):
           # Start listening for messages
           pass
   ```

3. **Register in main application**:
   ```python
   # app/main.py or app/__init__.py
   from app.channels.your_channel import YourChannel
   your_channel = YourChannel(message_queue, config)
   ```

## Command System

### Built-in Commands

| Command | Description | Channel Support |
|---------|-------------|-----------------|
| `/help` | Show help information | All channels |
| `/model` | Show current model info | All channels |
| `/tools` | List available tools | All channels |
| `/skills` | List available skills | All channels |
| `/config` | Show configuration | All channels |
| `/quit` | Exit the agent | CLI only |

### Command Structure

Commands follow a consistent pattern:

```
/<command> [argument1] [argument2]... [--option value]
```

Examples:
- `/model`
- `/help tools`
- `/config show --verbose`

### Adding New Commands

1. **Define command handler**:
   ```python
   # app/commands/your_command.py
   from app.message import IncomingMessage, OutgoingMessage
   from app.config import get_config
   
   async def handle_your_command(args: list, channel: Channel) -> str:
       config = get_config()
       # Process command logic
       return "Response message"
   
   def your_command_spec() -> dict:
       return {
           "name": "your_command",
           "description": "Description of your command",
           "usage": "/your_command [args]",
           "channels": ["cli", "discord"]  # Which channels support this
       }
   ```

2. **Register in command dispatcher**:
   ```python
   # app/commands/__init__.py
   from .your_command import handle_your_command, your_command_spec
   
   COMMANDS = {
       "your_command": {
           "handler": handle_your_command,
           "spec": your_command_spec(),
           "channels": ["cli", "discord", "websocket"]
       }
   }
   ```

3. **Update command parsing** in `app/agent.py` or dedicated command parser.

## Tool System

### Available Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `read_file` | Read file contents | `read_file(path="file.txt")` |
| `write_file` | Write to files | `write_file(path="file.txt", content="...")` |
| `bash` | Execute shell commands | `bash(command="ls -la")` |
| `web_fetch` | Fetch web content | `web_fetch(url="https://...")` |
| `get_skills_dir` | Locate skills | `get_skills_dir()` |
| `todo_add` | Add todo task | `todo_add(title="Task")` |
| `todo_list` | List todos | `todo_list()` |
| `todo_update` | Update todo status | `todo_update(task_id="1", status="done")` |
| `todo_clear` | Clear all todos | `todo_clear()` |

### Creating New Tools

1. **Create tool module**:
   ```python
   # app/tools/your_tool.py
   def your_tool_spec() -> dict:
       return {
           "type": "function",
           "function": {
               "name": "your_tool",
               "description": "Description of your tool",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "param1": {
                           "type": "string",
                           "description": "Parameter description"
                       }
                   },
                   "required": ["param1"]
               }
           }
       }
   
   async def your_tool(param1: str) -> str:
       try:
           # Tool implementation
           return f"Success: {param1}"
       except Exception as e:
           return f"Error: {str(e)}"
   ```

2. **Register in tool calls**:
   ```python
   # app/tool_calls.py
   from app.tools.your_tool import your_tool_spec, your_tool
   
   async def run_tool(tool_name: str, arguments: dict):
       if tool_name == "your_tool":
           return await your_tool(**arguments)
       # ... other tools
   
   def get_tool_specs():
       specs = []
       specs.append(your_tool_spec())
       # ... other tool specs
       return specs
   ```

## Skills System

### Available Skills

| Skill | Description | Location |
|-------|-------------|----------|
| **puppeteer** | Browser automation & web scraping | `app/skills/puppeteer/` |

### Skill Structure

```
app/skills/{skill-name}/
├── SKILL.md          # Skill documentation and instructions
├── __init__.py       # Skill implementation (optional)
└── examples/         # Usage examples (optional)
```

### Loading Skills

Skills are loaded dynamically by the agent using the `get_skills_dir` tool and processed as context for the LLM.

## Configuration

### Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `app/config.toml` | Agent settings | TOML |
| `.env` | API keys and secrets | Environment variables |
| `pyproject.toml` | Python project config | TOML |
| `codecrafters.yml` | CodeCrafters challenge config | YAML |

### Configuration Structure

```toml
# app/config.toml
[agent]
model = "deepseek/deepseek-v3.2"
max_iterations = 100
max_tokens = 32768

[channels]
cli.enabled = true
discord.enabled = false
websocket.enabled = false
api.enabled = false

[tools]
read_file.enabled = true
write_file.enabled = true
bash.enabled = true
web_fetch.enabled = true
```

## Extensibility Patterns

### 1. Plugin Architecture

```
plugins/
├── your_plugin/
│   ├── __init__.py
│   ├── channel.py
│   ├── tools.py
│   └── config.toml
└── plugin_manager.py
```

### 2. Middleware System

Middleware can intercept and modify messages:

```python
class LoggingMiddleware:
    async def pre_process(self, msg: IncomingMessage) -> IncomingMessage:
        logger.info(f"Incoming: {msg.content}")
        return msg
    
    async def post_process(self, msg: OutgoingMessage) -> OutgoingMessage:
        logger.info(f"Outgoing: {msg.content}")
        return msg
```

### 3. Event System

```python
from app.events import EventBus

event_bus = EventBus()
event_bus.subscribe("tool_called", log_tool_usage)
event_bus.publish("tool_called", {"tool": "read_file", "args": {...}})
```

## Usage Examples

### Starting the Agent

```bash
# CLI mode
./run.sh -p "Your prompt"

# With specific model
./run.sh -p "Your prompt" --model "anthropic/claude-3.5-sonnet"

# Silent/automated mode
./run.sh -p "Create a file" --silent
```

### Command Examples

```
> /model
Current model: deepseek/deepseek-v3.2
Provider: OpenRouter
Max tokens: 32768

> /tools
Available tools:
- read_file: Read file contents
- write_file: Write to files
- bash: Execute shell commands
- web_fetch: Fetch web content
- get_skills_dir: Locate skills directory
- todo_add: Add a todo task
- todo_list: List all tasks
- todo_update: Update task status
- todo_clear: Clear all todos

> /help channels
Available channels: CLI
Planned channels: Discord, WebSocket, API
```

## Future Development

### Planned Features

1. **Multi-channel support**
   - Discord bot integration
   - WebSocket real-time interface
   - REST API endpoints

2. **Enhanced tooling**
   - Database operations
   - Git operations
   - Docker/container management
   - Cloud service integration

3. **Advanced features**
   - Multi-agent collaboration
   - Long-term memory
   - Knowledge graph integration
   - Automated workflow creation

4. **Monitoring & observability**
   - Usage analytics
   - Performance metrics
   - Audit logging
   - Health checks

### Contribution Guidelines

1. **Code Style**: Follow existing patterns and PEP 8
2. **Testing**: Add tests for new features
3. **Documentation**: Update relevant docs
4. **Backwards Compatibility**: Maintain existing APIs
5. **Security**: Follow security best practices

## Getting Help

- **Issues**: GitHub Issues
- **Discussion**: GitHub Discussions
- **Documentation**: This file and README.md
- **Examples**: Check the `examples/` directory

---

*Last updated: $(date -I)*