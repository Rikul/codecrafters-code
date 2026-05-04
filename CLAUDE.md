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

Current tools: `read_file`, `write_file`, `bash`, `web_fetch`, `get_skills_dir`, `todo_add/list/update/clear`, `calculator`, `hackernews`, `websearch_text/images/videos/news/books`, `list/add/update/remove_scheduled_task`, `get_scheduled_task_output`.

`_HELPER_AGENT_TOOLS` in `tool_calls.py` is an explicit allowlist of tools available to `HelperAgent` (used internally by scheduled tasks). Scheduled task management tools are excluded to prevent recursion.

### System Context

On startup, `load_system_context()` (`app/helpers.py`) loads `app/sys_instructions.md` and prepends it as the system message to `self.messages`.

### Message Queue / Channel Architecture

`MessageQueue` (`app/message_queue.py`) holds two `asyncio.Queue`s (incoming/outgoing). Delivery functions are registered per `Channel` enum value. `BackgroundAgent.process_incoming()` consumes the incoming queue and drives `agent_loop()`; `process_outgoing()` dispatches outbound messages to registered delivery functions. This is the intended extension point for adding new channels.

Each channel should have its own `MessageQueue` instance to avoid cross-channel message routing bugs (e.g., a Telegram message being handled by the Discord agent).

### Scheduled Tasks

`ScheduledTasks` (`app/scheduled_tasks.py`) is a SQLite-backed task runner using the shared `APP_DB` (`~/.crafterscode/app.db`). It polls every 60 seconds, checks `next_run`, and executes due tasks via `HelperAgent`. Results are delivered to the configured channel via `MessageQueue`. Schema: `tasks` (id, name, prompt, enabled, repeat, interval_mins, next_run, last_run, delivery_channel, run_count, created_at) and `task_outputs` (id, name, prompt, output, status, duration_secs, timestamp). The `run()` coroutine is added to the `asyncio.gather` in `bg_server.py`.

## Testing Approach

Unit tests mock `app.cli_agent.Client` and `app.cli_agent.load_system_context` to isolate the agent loop logic. Integration tests in `tests/integration/` mock only the OpenAI HTTP client and run the full pipeline including `main()`, argparse, and agent construction. Tests use `pytest-asyncio` for async test functions.
