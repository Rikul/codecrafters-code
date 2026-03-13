import subprocess
import sys

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
    print(f"func: bash, command: {command}", file=sys.stderr)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr}"

    except Exception as e:
        return f"Error executing command: {e}"
