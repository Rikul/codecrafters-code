A CodeCrafters challenge project implementing an AI agent with tool calling capabilities, built for the ["Build Your own Claude Code" Challenge](https://codecrafters.io/challenges/claude-code).

## Overview

An AI agent that can parse and execute user prompts, interact with the file system, run shell commands, fetch web content, and track tasks. Built using the OpenRouter API (defaulting to DeepSeek) via the OpenAI Python client.

- **Interactive CLI**: REPL mode for multi-turn agent sessions
- **Tool Calling**: File operations, shell commands, web fetching, and task tracking
- **Skills System**: Skills located in `app/skills/` directory (e.g., `puppeteer`)
- **Background Agent**: Message queue and channel architecture for multi-channel delivery (Telegram, Discord, etc.)
- **Telegram Integration**: Built-in Telegram bot channel (`app/telegram_channel.py`) for receiving and sending messages
- **Persistent Message History**: SQLite-backed history at `~/.crafterscode/history.db`, stored per channel with token estimates
- **Context Window Trimming**: Automatically trims conversation history to the last 100 messages (preserving the system message) to stay within model context limits


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

Set `LLM_API_KEY` in a `.env` file or as an environment variable. Alternatively, set `api_key` directly in `config.toml` (env var takes precedence):

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
api_key = ""  # fallback if LLM_API_KEY env var is not set

[telegram]
BOT_TOKEN = ""
ALLOW_FROM = []  # List of allowed Telegram user IDs (integers).
```

Message history is stored in `~/.crafterscode/history.db` (SQLite). Each channel maintains its own history with estimated token counts per message.

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

**Built-in Telegram commands:** `/help` — list available commands; `/whoami` — show your Telegram user ID (useful for configuring `ALLOW_FROM`).

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

Unit tests mock `app.cli_agent.Client` and `app.cli_agent.load_system_context` (see `tests/test_startup.py`). Integration tests mock only the OpenAI HTTP client and run the full pipeline including `main()` and argparse.

## Adding New Tools

Tools use a class-based system with the `Tool` abstract base class (`app/tools/tool.py`).

1. Create `app/tools/my_tool.py` subclassing `Tool`
2. Register in `app/tool_calls.py` `tool_registry`

```python
from .tool import Tool

class MyTool(Tool):
    @staticmethod
    def spec() -> dict:
        return {
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

    @staticmethod
    def call(param: str) -> str:
        return "result"
```

## License

Part of the CodeCrafters "Build Your own Claude Code" Challenge. See [codecrafters.io](https://codecrafters.io) for details.
