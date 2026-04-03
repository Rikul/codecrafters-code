A CodeCrafters challenge project implementing an AI agent with tool calling capabilities, built for the ["Build Your own Claude Code" Challenge](https://codecrafters.io/challenges/claude-code).

## Overview

An AI agent that can parse and execute user prompts, interact with the file system, run shell commands, fetch web content, and track tasks. Built using the OpenRouter API (defaulting to DeepSeek) via the OpenAI Python client.

- **Interactive CLI**: REPL mode for multi-turn agent sessions
- **Tool Calling**: File operations, shell commands, web fetching, and task tracking
- **Skills System**: Skills located in `app/skills/` directory (e.g., `puppeteer`)
- **Background Agent**: Message queue and channel architecture for multi-channel delivery (Telegram, Discord, etc.)
- **Telegram Integration**: Built-in Telegram bot channel (`app/telegram_channel.py`) for receiving and sending messages


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

[telegram]
BOT_TOKEN = ""
ALLOW_FROM = []  # List of allowed Telegram user IDs (integers). Empty list means allow all.
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

### Background Agent with Telegram

To run the agent as a Telegram bot, set your `BOT_TOKEN` and optionally restrict access by Telegram user ID in `~/.crafterscode/config.toml`:

```toml
[telegram]
BOT_TOKEN = "123456:ABC-your-bot-token"
ALLOW_FROM = [123456789]  # Telegram user IDs allowed to interact.
```

Then start the background agent:

```bash
./run.sh background
```

The agent will listen for messages on Telegram and respond via the bot. Responses are routed back to the same chat that sent the message.

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
