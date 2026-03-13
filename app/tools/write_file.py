import os
import sys
from app.config import Config
from app.display import log

write_file_tool_spec = {
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

def write_file(file_path: str, content: str) -> str:
    log.info(f"write_file, file_path: {file_path}")

    ws_file_path = Config.WORKSPACE_DIR / file_path

    # Validate path stays within workspace
    try:
        ws_file_path.resolve().relative_to(Config.WORKSPACE_DIR.resolve())
    except ValueError:
        return f"Error: Path {file_path} attempts to write outside workspace"

    try:
    
      os.makedirs(ws_file_path.parent, exist_ok=True)

      with open(ws_file_path, "w", encoding = "utf-8") as f:
          f.write(content)

    except Exception as e:
        return f"Error writing to file {ws_file_path}: {e}"
      
    return f"Successfully wrote to file: {ws_file_path}"