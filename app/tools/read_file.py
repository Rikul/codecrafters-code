import os
import sys


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
    print(f"func: read_file, file_path: {file_path}", file=sys.stderr)

    if not os.path.exists(file_path):
        return f"Error: file {file_path} does not exist"
    
    with open(file_path, encoding = "utf-8") as f:
        return f.read()
