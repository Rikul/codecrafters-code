A CodeCrafters challenge project implementing an AI agent with tool calling capabilities, built for the ["Build Your own Claude Code" Challenge](https://codecrafters.io/challenges/claude-code).

## Overview

- Parse and execute user prompts
- Make decisions about which tools to use
- Interact with the file system (read, write)
- Execute shell commands
- Fetch web content
- Track tasks with todo system

The implementation uses the OpenRouter API (defaulting to DeepSeek) via the OpenAI Python client and follows the CodeCrafters challenge requirements.

## Features

- **Interactive CLI**: REPL mode for multi-turn agent sessions
- **Tool Calling**: Multiple tools for file operations, web fetching, and shell commands
  - `read_file`: Read contents of files
  - `write_file`: Write content to files (with safety checks)
  - `bash`: Execute shell commands
  - `web_fetch`: Retrieve content from URLs
  - `get_skills_dir`: Locate skills directory
  - **Todo Tools**: `todo_add`, `todo_list`, `todo_update`, `todo_clear` for task tracking
- **Skills System**: Skills located in `app/skills/` directory (e.g., `puppeteer`)
- **System Context Loading**: Loads personality and instructions from `app/system.md/` on startup
- **Background Agent**: Message queue and channel architecture for multi-channel delivery (Telegram, Discord, Web, etc.)
- **Telegram Integration**: Built-in Telegram bot channel (`app/telegram_channel.py`) for receiving and sending messages
- **Web Server**: HTTP server (`app/server.py`) for web-based channel delivery

## Prerequisites

- Python 3.12 or higher
- `uv` package manager
- OpenRouter API key (or any OpenAI-compatible API)

## Installation

```bash
uv sync
```

## Configuration

### API Key (Required)

Set `LLM_API_KEY` in a `.env` file or as an environment variable:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1  # optional override
```

### Agent Config

Config lives at `~/.crafterscode/config.toml` and is created automatically on first run with defaults:

```toml
model = "deepseek/deepseek-v3.2"
max_iterations = 100
max_tokens = 32768
base_url = "https://openrouter.ai/api/v1"
```

## Usage

```bash
./run.sh cli -p "your prompt here"

# Flags
-p, --prompt          Initial prompt (required)
-y, --auto-approve    Skip tool permission prompts
-x, --no-repl         Exit after initial prompt (no REPL)
-s, --silent          Suppress output, implies -y -x
-i, --max-iterations  Max agentic loop iterations (default: 100)
```

### Examples

```bash
# Interactive REPL session
./run.sh cli -p "List all Python files in the current directory"

# Single-shot, auto-approved
./run.sh cli -p "Create a hello world script" -y -x

# Silent mode
./run.sh cli -p "Summarize this repo" -s
```

## Architecture

### Agent Loop

`CliAgent` (`app/cli_agent.py`) and `BackgroundAgent` (`app/background_agent.py`) share the same loop:
1. Append user message to `self.messages`
2. Call `chat.completions.create` with tool specs
3. If `tool_calls`: optionally ask permission, run each via `run_tool()`, append results, loop
4. If no tool calls: print/send content, break on `finish_reason == "stop"`

`CliAgent` prints to stdout and prompts stdin for permission. `BackgroundAgent` routes messages through `MessageQueue` + `Channel` for multi-channel delivery.

### Tool System

Tools are registered in `app/tool_calls.py` (`tool_registry` dict: name → `{spec, func}`). Each tool in `app/tools/` exports a function and an OpenAI-format spec. `run_tool()` dispatches by name and restores `os.getcwd()` after each call.

### System Context

`load_system_context()` (`app/helpers.py`) loads markdown files from `app/system.md/` in order: `self.md`, `user.md`, `workspace.md`, `tool_instructions.md`, `skills.md`. Combined content becomes the system message.

### Message Queue / Channel Architecture

`MessageQueue` (`app/message_queue.py`) holds two `asyncio.Queue`s (incoming/outgoing). Delivery functions are registered per `Channel` enum value. This is the extension point for adding new delivery channels.

## Project Structure

```
.
├── app/
│   ├── tools/              # Tool implementations
│   ├── skills/             # Skill definitions (e.g., puppeteer/)
│   ├── system.md           # System context markdown (loaded on startup)
│   ├── cli_agent.py        # Interactive CLI agent
│   ├── background_agent.py # Background agent with message queue
│   ├── cli.py              # REPL input loop
│   ├── channel.py          # Channel enum
│   ├── message.py          # Message dataclasses
│   ├── message_queue.py    # Async message queue
│   ├── telegram_channel.py # Telegram bot delivery channel
│   ├── server.py           # HTTP server for web channel
│   ├── tool_calls.py       # Tool registry and dispatcher
│   ├── helpers.py          # System context loader
│   ├── display.py          # Logging/display utilities
│   ├── config.py           # Config loader
│   ├── setup.py            # Home directory setup
│   ├── client.py           # OpenAI client factory
│   └── main.py             # Entry point (argparse, subcommands)
├── tests/
│   └── integration/        # Full-pipeline integration tests
├── pyproject.toml
├── run.sh
└── README.md
```

## Testing

```bash
# All tests
uv run pytest

# Single file
uv run pytest tests/test_agent.py

# Integration tests
uv run pytest tests/integration/

# With coverage
uv run pytest --cov=app --cov-report=term-missing
```

Unit tests mock `app.cli_agent.Client` and `app.cli_agent.load_system_context`. Integration tests mock only the OpenAI HTTP client and run the full pipeline including `main()` and argparse.

## Adding New Tools

1. Create `app/tools/my_tool.py` with a function and OpenAI-format spec dict
2. Register in `app/tool_calls.py` `tool_registry`

```python
MY_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "...",
        "parameters": {
            "type": "object",
            "properties": {"param": {"type": "string", "description": "..."}},
            "required": ["param"]
        }
    }
}

def my_tool(param: str) -> str:
    return "result"
```

## License

Part of the CodeCrafters "Build Your own Claude Code" Challenge. See [codecrafters.io](https://codecrafters.io) for details.
