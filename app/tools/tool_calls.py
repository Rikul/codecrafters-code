from app.tools.read_file import read_file, read_file_tool_spec
from app.tools.write_file import write_file, write_file_tool_spec
from app.tools.bash import bash, bash_tool_spec

tool_specs = {}

tool_specs["read_file"] = read_file_tool_spec
tool_specs["write_file"] = write_file_tool_spec
tool_specs["bash"] = bash_tool_spec

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