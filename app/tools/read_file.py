import os
import sys
from app.display import log

read_file_tool_spec = {
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

def read_file(file_path: str) -> str:
    log.info(f"read_file, file_path: {file_path}")

    if not os.path.exists(file_path):
        return f"Error: file {file_path} does not exist"
    
    try:

      with open(file_path, encoding = "utf-8") as f:
          return f.read()

    except Exception as e:
        return f"Error reading file {file_path}: {e}"
    
    return ""