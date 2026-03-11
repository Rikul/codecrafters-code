import os
import sys

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
    print(f"func: write_file, file_path: {file_path}", file=sys.stderr)

    with open(file_path, "w", encoding = "utf-8") as f:
        f.write(content)
    
    return f"Successfully wrote to file {file_path}"