A CodeCrafters challenge project implementing an AI agent with tool calling capabilities, built for the ["Build Your own Claude Code" Challenge](https://codecrafters.io/challenges/claude-code).

## 🌟 Overview

- Parse and execute user prompts
- Make decisions about which tools to use
- Interact with the file system (read, write)
- Execute shell commands
- Fetch web content
- Track tasks with todo system

The implementation uses the OpenRouter API with OpenAI's client library and follows the CodeCrafters challenge requirements.

## ✨ Features

- **Interactive CLI**: Command-line interface for interacting with the agent
- **Tool Calling**: Multiple tools for file operations, web fetching, and shell commands
  - `read_file`: Read contents of files
  - `write_file`: Write content to files (with safety checks)
  - `bash`: Execute shell commands
  - `web_fetch`: Retrieve content from URLs
  - `get_skills_dir`: Locate skills directory
  - **Todo Tools**: `todo_add`, `todo_list`, `todo_update`, `todo_clear` for task tracking
- **Skills System**: 
  - `puppeteer`: Browser Automation & Web Scraping
  - Skills located in `app/skills/` directory
- **System Context Loading**: Load personality and instructions from `system/` and `skills/` directories
- **Error Handling**: Graceful error recovery and user-friendly messages
- **Workspace Support**: Configurable workspace for persistent storage

## 📋 Prerequisites

- Python 3.12 or higher
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

### 1. API Configuration (Required)

Create a `.env` file in the project root with your OpenRouter credentials:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1  # Optional, default is set
```

**Note**: The `LLM_API_KEY` is **required**. You can obtain one from [OpenRouter](https://openrouter.ai/).

### 2. Agent Configuration

Configure the agent behavior in `app/config.toml`:

```toml
model = "deepseek/deepseek-v3.2"  # Model to use
max_iterations = 100              # Maximum iterations per prompt
max_tokens = 32768                # Maximum tokens per response
```

### 3. Workspace Configuration (Optional)

The workspace provides persistent storage across sessions. Configure workspace settings as needed.

## 🏃‍♂️ Usage

### Running the Agent

```bash
./run.sh --help
usage: python3 -m app.main [-h] -p PROMPT [--auto-approve] [--no-repl] [--max-iterations N] [--silent]

options:
  -h, --help           show this help message and exit
  -p, --prompt PROMPT  The initial prompt for the agent
  --auto-approve       Allow the agent to call tools without asking for permission
  --no-repl            Run the agent with the initial prompt and then exit without starting the REPL
  --max-iterations N   The maximum number of iterations the agent will run before stopping (default: 100)
  --silent             Suppress all output except the final response (implies --auto-approve --no-repl)
```

### Basic Examples

```bash
# Interactive session with a prompt
./run.sh -p "Your prompt here"

# Single execution without REPL
./run.sh --no-repl -p "List all Python files in the current directory"

# Silent mode (no interactive questions, single execution)
./run.sh --silent -p "Create a README.md file"

# With custom iteration limit
./run.sh -p "Complex task" --max-iterations 50
```

### Example Session

```bash
$ ./run.sh -p "Create a Python script that calculates Fibonacci numbers"
```

The agent will:
1. Analyze your request
2. Decide which tools to use
3. Create the file
4. Report back with the results

### Todo System Example

The agent can track tasks using the todo tools:

```bash
$ ./run.sh -p "Plan and execute a project setup"
```

The agent might:
1. Add todo tasks using `todo_add`
2. Work on tasks and update status with `todo_update`
3. List progress with `todo_list`
4. Clear tasks when done with `todo_clear`

## 🔧 Available Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `read_file` | Read file contents | Read configuration files |
| `write_file` | Write to files | Create scripts, documentation |
| `bash` | Execute shell commands | File operations, installations |
| `web_fetch` | Fetch web content | Research, data collection |
| `get_skills_dir` | Locate skills directory | Load specialized skills |
| `todo_add` | Add a todo task | Project planning |
| `todo_list` | List all tasks | Progress tracking |
| `todo_update` | Update task status | Mark tasks as done |
| `todo_clear` | Clear all todos | Reset task tracking |

## 🧪 Skills System

### Using Skills

Skills provide expert guidance for specialized tasks. The agent can load skills from `app/skills/{skill-name}/SKILL.md`.

**Available Skills:**
- **puppeteer**: Browser automation, web scraping, screenshot capture, PDF generation

### Adding New Skills

To add a new skill:
1. Create directory `app/skills/{skill-name}/`
2. Add `SKILL.md` with skill instructions
3. The agent can load it using `get_skills_dir` tool

## 🧪 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_agent.py

# Run with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=app --cov-report=term-missing
```

### Test Structure

- **Unit Tests**: Test individual components and tools
- **Integration Tests**: Test end-to-end functionality in `tests/integration/`
- **Mocking**: External API calls are mocked to avoid actual API usage

## 🔧 Development

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

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd codecrafters-claude-code

# Install with development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run ruff format app/ tests/

# Lint code
uv run ruff check app/ tests/
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your `.env` file contains `LLM_API_KEY=your_key_here`
2. **Python Version**: Ensure you have Python 3.12 or higher (`python --version`)
3. **Configuration Issues**: Check `app/config.toml` exists with proper settings
4. **Permission Errors**: Make sure `run.sh` is executable (`chmod +x run.sh`)
5. **Import Errors**: Run from project root or use `./run.sh` script

### Debug Mode

For debugging, you can run with verbose output:

```bash
# Direct execution with debug
uv run --project . --quiet -m app.main -p "Your prompt" --max-iterations 5
```

## 📝 Project Structure

```
.
├── app/                    # Application code
│   ├── skills/            # Skill definitions
│   │   └── puppeteer/     # Puppeteer skill
│   ├── tools/             # Tool implementations
│   ├── config.toml        # Agent configuration
│   ├── config.py          # Configuration loader
│   ├── agent.py           # Main agent logic
│   └── main.py            # CLI entry point
├── tests/                 # Test suite
├── .env                   # API credentials (create)
├── config.toml            # Model settings
├── pyproject.toml         # Python project config
├── run.sh                 # Main execution script
└── README.md              # This file
```

## 📝 Future Improvements

- Implement retry logic for API calls
- Add more useful tools and skills (todo tasks, mcp, etc.)
- Session persistence
- Add streaming responses for better UX
- Add support for additional LLM providers
- Implement conversation history
- Add file watching capabilities
- Create GUI/web interface

## 📄 License

This project is part of the CodeCrafters "Build Your own Claude Code" Challenge. See the [CodeCrafters website](https://codecrafters.io) for more information about their challenges and licensing.

## 🙏 Acknowledgments

- [CodeCrafters](https://codecrafters.io) for the challenge platform
- [OpenRouter](https://openrouter.ai) for LLM API access
- [OpenAI](https://openai.com) for the client library interface
- All contributors and testers