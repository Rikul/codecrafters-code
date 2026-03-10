from app.tools.read_file import read_file

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

def run_tool(tool_name: str, tool_args: dict):
    
    if tool_name == "read_file":
        file_path = tool_args["file_path"]
        return read_file(file_path=file_path)
    else:
        return f"Error: unknown tool {tool_name}"