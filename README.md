
A CodeCrafters challenge project implementing an AI agent with tool calling capabilities, built for the ["Build Your own Claude Code" Challenge](https://codecrafters.io/challenges/claude-code).

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
- **Skills**: 
  - `puppeteer`: Browser Automation & Web Scraping
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
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1  # Optional, default is set
LLM_MODEL=deepseek/deepseek-v3.2
```

**Note**: The `LLM_API_KEY` is **required**. You can obtain one from [OpenRouter](https://openrouter.ai/).

## 🏃‍♂️ Usage

### Running Locally

The preferred way to run the agent locally:

```bash
./run.sh --help
usage: python3 -m app.main [-h] -p PROMPT [--auto-approve] [--no-repl] [--workspace path] [--max-iterations N]

options:
  -h, --help           show this help message and exit
  -p, --prompt PROMPT  The initial prompt for the agent
  --auto-approve       Allow the agent to call tools without asking for permission
  --no-repl            Run the agent with the initial prompt and then exit without starting the REPL
  --workspace path     The directory where the agent will work (default: current directory)
  --max-iterations N   The maximum number of iterations the agent will run before stopping (default: 100)
```

```bash
./run.sh -p "Your prompt here"
```

```bash
./run.sh --no-repl -p "List all Python files in the current directory" --workspace ~/src
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
- Add useful tools and skills
- Session persistence
- Add streaming responses for better UX
- Add comprehensive unit tests
- Add response format option (e.g. json, markdown, plain text)
- Add non-interactive mode where the agent runs without user input
- Refactor config to toml