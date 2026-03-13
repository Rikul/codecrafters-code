
A CodeCrafters challenge project implementing a Claude Code-like AI agent with tool calling capabilities, built for the ["Build Your own Claude Code" Challenge](https://codecrafters.io/challenges/claude-code).

## 🌟 Overview

- Parse and execute user prompts
- Make decisions about which tools to use
- Interact with the file system (read, write)
- Execute shell commands
- Fetch web content

The implementation uses the OpenRouter API with OpenAI's client library and follows the CodeCrafters challenge requirements.

## ✨ Features

- **Interactive CLI**: Command-line interface for interacting with the agent
- **Tool Calling**: Multiple tools for file operations, web fetching, and shell commands
  - `read_file`: Read contents of files
  - `write_file`: Write content to files (with safety checks)
  - `bash`: Execute shell commands
  - `web_fetch`: Retrieve content from URLs
- **System Context Loading**: Load personality and instructions from `system/` and `skills/` directories
- **Error Handling**: Graceful error recovery and user-friendly messages
- **Structured Output**: Rich terminal formatting for better UX

## 📋 Prerequisites

- Python 3.14 or higher
- `uv` package manager (recommended) or pip
- OpenRouter API key

## 🚀 Installation

### Using uv (Recommended)

```bash
# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

### Using pip

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file in the project root with your OpenRouter credentials:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1  # Optional, default is set
```

**Note**: The `OPENROUTER_API_KEY` is **required**. You can obtain one from [OpenRouter](https://openrouter.ai/).

## 🏃‍♂️ Usage

### Running Locally

The preferred way to run the agent locally:

```bash
./your_program.sh -p "Your prompt here"
```

For example:

```bash
./your_program.sh -p "List all Python files in the current directory"
```

This script sets up the proper `PYTHONPATH` and environment, then runs `uv run -m app.main`.

### Direct uv command (equivalent)

```bash
uv run --project . --quiet -m app.main -p "Your prompt here"
```

### Example Session

```bash
$ ./your_program.sh -p "Create a Python script that calculates Fibonacci numbers"
```

The agent will:
1. Analyze your request
2. Decide which tools to use
3. Create the file
4. Report back with the results

### Adding New Tools

To add a new tool:

1. Create a new file in `app/tools/` (e.g., `my_tool.py`)
2. Define the tool specification and implementation
3. Register it in `app/tools/tool_calls.py` (update `run_tool()` function)
4. Add tests if applicable

Example tool structure:

```python
def my_tool_spec():
    return {
        "type": "function",
        "function": {
            "name": "my_tool",
            "description": "Tool description",
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

def my_tool(param1: str) -> str:
    """Tool implementation."""
    try:
        # Do something
        return "Success message"
    except Exception as e:
        return f"Error: {str(e)}"
```

## 📝 Future Improvements

- Implement retry logic for API calls
- Add more tools (git operations, code search, etc.)
- Session persistence
- Add streaming responses for better UX
- Add comprehensive unit tests
