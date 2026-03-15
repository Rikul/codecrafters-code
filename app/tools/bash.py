import subprocess
from app.display import log

bash_tool_spec = {
  "type": "function",
  "function": {
    "name": "bash",
    "description": "Execute a shell command",
    "parameters": {
      "type": "object",
      "required": ["command"],
      "properties": {
        "command": {
          "type": "string",
          "description": "The command to execute"
        }
      }
    }
  }
}

def bash(command: str) -> str:
    log.info(f"bash, command: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr}"

    except Exception as e:
        return f"Error executing command: {e}"
