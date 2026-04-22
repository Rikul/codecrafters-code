# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **CodeCrafters challenge** project implementing a Python-based AI agent CLI ("crafterscode") that uses an OpenAI-compatible API (defaulting to OpenRouter/DeepSeek) via the `openai` Python SDK. The agent supports interactive REPL mode, silent/non-interactive mode, and a background agent architecture for multi-channel messaging.

## Running & Development

```bash
# Run the CLI agent
./run.sh cli -p "your prompt here"

# Run with auto-approve (no permission prompts) and exit after response
./run.sh cli -p "your prompt" -y -x

# Run in silent mode (suppresses output, implies --auto-approve --no-repl)
./run.sh cli -p "your prompt" -s

# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/test_agent.py

# Run a single test
uv run pytest tests/test_agent.py::test_agent_loop_adds_user_message

# Run integration tests
uv run pytest tests/integration/
```

The project uses `uv` for dependency management. No compile step is needed.

## Configuration

Config lives at `~/.crafterscode/config.toml` (created automatically on first run with defaults). Key fields:
- `model` — LLM model string (default: `"deepseek/deepseek-v3.2"`)
- `max_iterations` — max agentic loop iterations (default: `100`)
- `max_tokens` — max tokens per LLM call (default: `32768`)
- `base_url` — API base URL (default: `"https://openrouter.ai/api/v1"`)

Environment variables: `LLM_API_KEY` (required), `LLM_BASE_URL` (optional override).

## Architecture

### Agent Loop

Both `CliAgent` (`app/cli_agent.py`) and `BackgroundAgent` (`app/background_agent.py`) share the same agentic loop pattern:
1. Append user message to `self.messages`
2. Call `chat.completions.create` with tool specs
3. If response has `tool_calls`: optionally ask permission, run each tool via `run_tool()`, append tool results, loop again
4. If response has no tool calls: print/send content, break if `finish_reason == "stop"`

The difference: `CliAgent` prints to stdout and prompts stdin for permission; `BackgroundAgent` routes messages through `MessageQueue` + `Channel` for multi-channel delivery (Telegram, Discord, Web, etc.).

### Tool System

Tools are registered in `app/tool_calls.py` in `tool_registry` — a dict mapping tool name → `{spec, func}`. Each tool in `app/tools/` exports a function and an OpenAI-format tool spec dict. `run_tool()` dispatches by name and restores `os.getcwd()` after each call.

Current tools: `read_file`, `write_file`, `bash`, `web_fetch`, `get_skills_dir`, `todo_add/list/update/clear`.

### System Context

On startup, `load_system_context()` (`app/helpers.py`) loads `app/sys_instructions.md` and prepends it as the system message to `self.messages`.

### Message Queue / Channel Architecture

`MessageQueue` (`app/message_queue.py`) holds two `asyncio.Queue`s (incoming/outgoing). Delivery functions are registered per `Channel` enum value. `BackgroundAgent.process_incoming()` consumes the incoming queue and drives `agent_loop()`; `process_outgoing()` dispatches outbound messages to registered delivery functions. This is the intended extension point for adding new channels.

## Testing Approach

Unit tests mock `app.cli_agent.Client` and `app.cli_agent.load_system_context` to isolate the agent loop logic. Integration tests in `tests/integration/` mock only the OpenAI HTTP client and run the full pipeline including `main()`, argparse, and agent construction. Tests use `pytest-asyncio` for async test functions.
