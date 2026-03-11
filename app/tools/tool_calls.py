from app.tools.read_file import read_file
from app.tools.write_file import write_file
from app.tools.bash import bash

tool_specs = {"read_file": None, "write_file": None, "bash": None}

tool_specs["read_file"] = {
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Read and return the contents of a file",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "The path to the file to read"
        }
      },
      "required": ["file_path"]
    }
  }
}

tool_specs["write_file"] = {
  "type": "function",
  "function": {
    "name": "write_file",
    "description": "Write content to a file",
    "parameters": {
      "type": "object",
      "required": ["file_path", "content"],
      "properties": {
        "file_path": {
          "type": "string",
          "description": "The path of the file to write to"
        },
        "content": {
          "type": "string",
          "description": "The content to write to the file"
        }
      }
    }
  }
}

tool_specs["bash"] = {
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

def run_tool(tool_name: str, tool_args: dict):

    if tool_name == "read_file":
        file_path = tool_args["file_path"]
        return read_file(file_path=file_path)
    
    elif tool_name == "write_file":
        file_path = tool_args["file_path"]
        content = tool_args["content"]
        return write_file(file_path=file_path, content=content)
    
    elif tool_name == "bash":
        command = tool_args["command"]
        return bash(command=command)
    
    else:
        return f"Error: unknown tool {tool_name}"