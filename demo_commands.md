# Command System Demo

## Overview

The crafterscode agent now has a comprehensive command system that allows users to interact with the agent using special commands starting with `/`. This system is designed to be extensible and reusable across different channels.

## Available Commands

### 1. `/model` - Model Configuration
**Description**: Show or change the current AI model

**Usage**:
```
/model [show|set] [--verbose]
```

**Examples**:
- `/model` - Show current model
- `/model show` - Show current model (explicit)
- `/model show --verbose` - Show detailed model configuration
- `/model set "anthropic/claude-3.5-sonnet"` - Change model (implementation pending)

**Sample Output**:
```
🤖 Current model: deepseek/deepseek-v3.2
```

With verbose flag:
```
📊 Model Configuration 📊
├─ Model: deepseek/deepseek-v3.2
├─ Base URL: https://openrouter.ai/api/v1
├─ Max Tokens: 32768
└─ Max Iterations: 200
```

### 2. `/help` - Help System
**Description**: Show help for commands

**Usage**:
```
/help [command|category]
```

**Examples**:
- `/help` - Show general help
- `/help model` - Show help for /model command
- `/help tools` - Show tools category commands
- `/help system` - Show system category commands

### 3. `/config` - Configuration Management
**Description**: Show or update configuration

**Usage**:
```
/config [show|get|set] [key] [value] [--verbose]
```

**Examples**:
- `/config` - Show all configuration
- `/config get model` - Get specific config value
- `/config set model "anthropic/claude-3.5-sonnet"` - Set config value (implementation pending)

### 4. `/tools` - Tool Management
**Description**: List available tools or show tool details

**Usage**:
```
/tools [list|info] [tool_name]
```

**Examples**:
- `/tools` - List available tools
- `/tools list` - List available tools (explicit)
- `/tools info bash` - Show detailed info about bash tool

### 5. `/skills` - Skill Management
**Description**: List available skills or show skill details

**Usage**:
```
/skills [list|info] [skill_name]
```

**Examples**:
- `/skills` - List available skills
- `/skills info puppeteer` - Show details about puppeteer skill

### 6. `/quit` - Exit Agent
**Description**: Quit the agent

**Usage**:
```
/quit [--force]
```

**Examples**:
- `/quit` - Gracefully quit
- `/quit --force` - Force quit

## Command Syntax

### Basic Structure
```
/command [argument1] [argument2]... [--option value] [--flag]
```

### Features:
1. **Positional Arguments**: Space-separated values
   - `/help model`
   - `/tools info bash`

2. **Keyword Arguments**: Options with `--`
   - `/model show --verbose`
   - `/config set model "value" --dry-run`

3. **Boolean Flags**: Options without values
   - `/quit --force`
   - `/model --verbose`

4. **Quoted Values**: Support for spaces in values
   - `/model set "anthropic/claude-3.5-sonnet"`

## Architecture

### Command System Components

```
┌─────────────────────────────────────────────────────┐
│                 Command Input                       │
│                 (e.g., "/model show --verbose")     │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                 Command Parser                      │
│                 • Validates syntax                  │
│                 • Extracts arguments/options        │
│                 • Handles quotes and escaping       │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                 Command Dispatcher                  │
│                 • Looks up command in registry      │
│                 • Validates channel permissions     │
│                 • Executes command handler          │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                 Command Handler                     │
│                 • Executes command logic            │
│                 • Returns formatted response        │
└─────────────────────────────────────────────────────┘
```

### Command Registry

Commands are registered in a central registry with metadata:
- **Name**: Primary command name
- **Aliases**: Alternative names (e.g., `h` for `help`)
- **Description**: Brief description
- **Usage**: Syntax examples
- **Category**: Organization category (system, tools, config, etc.)
- **Channels**: Which channels support this command
- **Permissions**: Required permissions (if any)

### Extensibility

#### Adding New Commands

1. **Create command handler**:
```python
async def handle_your_command(args, kwargs, channel, user_identity):
    # Command logic here
    return "Response message"
```

2. **Register command**:
```python
_registry.register(Command(
    name="yourcommand",
    handler=handle_your_command,
    description="Description of your command",
    usage="/yourcommand [args] [--options]",
    category=CommandCategory.YOUR_CATEGORY,
    channels=[Channel.CLI, Channel.DISCORD],
))
```

#### Adding New Categories

1. **Extend CommandCategory enum**:
```python
class CommandCategory(str, Enum):
    # ... existing categories
    YOUR_CATEGORY = "your_category"
```

## Usage Examples

### Interactive Session
```
> /help
📚 Available Commands 📚

Type /help <command> for detailed help on a specific command.
Type /help <category> to see commands in a category.

📂 Categories:
  system: 3 commands
  tools: 2 commands
  config: 1 commands

🔧 System Commands:
  /help - Show this help message
  /model - Show or change the current model
  /config - Show or update configuration

💡 Tip: Commands start with '/' and support arguments and flags (--flag value).

> /model
🤖 Current model: deepseek/deepseek-v3.2

> /model show --verbose
📊 Model Configuration 📊
├─ Model: deepseek/deepseek-v3.2
├─ Base URL: https://openrouter.ai/api/v1
├─ Max Tokens: 32768
└─ Max Iterations: 200

> /tools
🛠️ Available Tools:
  bash: Execute shell commands...
  get_skills_dir: Get the path to the skills directory...
  read_file: Read and return the contents of a file...
  todo_add: Add a new task to the todo list...
  todo_clear: Todos are done, clear all todos...
  todo_list: List all tasks and their statuses...
  todo_update: Update the status of a task...
  web_fetch: Fetch and return the contents of a web page...
  write_file: Write content to a file...

> /skills
🧠 Available Skills:
  puppeteer

> /quit
👋 Goodbye! Use Ctrl+C to exit.
```

### Channel Support

The command system is designed to work across multiple channels:

1. **CLI**: Fully supported (current implementation)
2. **Discord**: Planned (commands like `/model` would work in Discord)
3. **WebSocket**: Planned
4. **API**: Planned (REST endpoints for commands)

Each command specifies which channels it supports.

## Implementation Details

### File Structure
```
app/
├── commands.py              # Command system implementation
├── agent.py                # Updated to handle commands
├── __init__.py            # Exports command system
└── config.py              # Configuration access
```

### Key Changes

1. **Agent Integration**:
   - `agent.py` now checks if input is a command
   - Commands bypass normal LLM processing
   - Command responses are sent directly to user

2. **Command System**:
   - Central registry for all commands
   - Parser for command syntax
   - Dispatcher for command execution
   - Extensible architecture

3. **Reusability**:
   - Commands work across channels
   - Easy to add new commands
   - Consistent API for all commands

## Testing

### Manual Testing
```bash
# Run the agent
./run.sh -p "Hello"

# In the REPL, try commands:
> /model
> /help
> /tools
> /skills
> /quit
```

### Automated Tests
```python
# Unit tests for command parsing
python3 test_commands_simple.py

# Integration tests
python3 test_integration.py
```

## Future Improvements

### Planned Features
1. **Command Aliases**: Short forms (e.g., `/m` for `/model`)
2. **Tab Completion**: For commands and arguments
3. **Command History**: Navigate previous commands
4. **Permissions System**: Role-based access control
5. **Plugin System**: Load commands from external modules
6. **Web Interface**: GUI for command execution
7. **Command Scripting**: Batch execution of commands
8. **Audit Logging**: Track all command executions

### Additional Commands
- `/history` - Show interaction history
- `/status` - Show agent status
- `/memory` - Manage conversation memory
- `/plugins` - Manage plugins
- `/channels` - Manage communication channels
- `/users` - User management (for multi-user environments)

## Conclusion

The command system provides a powerful, extensible way to interact with the crafterscode agent. The `/model` command demonstrates the system's capabilities, showing how users can query and potentially modify the AI model configuration. The system is designed to be reusable across different communication channels, making it a foundation for future expansion.

The implementation follows clean architecture principles, with clear separation between parsing, dispatching, and execution. This makes it easy to add new commands, support new channels, and extend functionality as needed.

---

*Last updated: $(date -I)*
*See also: `agents.md` for architecture documentation*