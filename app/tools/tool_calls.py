from app.tools.read_file import read_file, read_file_tool_spec
from app.tools.write_file import write_file, write_file_tool_spec
from app.tools.bash import bash, bash_tool_spec
from app.tools.web_fetch import web_fetch, web_fetch_tool_spec
import os

tool_registry = {
    "read_file":    { "spec": read_file_tool_spec,  "func": read_file },
    "write_file":   { "spec": write_file_tool_spec, "func": write_file },
    "bash":         { "spec": bash_tool_spec,       "func": bash },
    "web_fetch":    { "spec": web_fetch_tool_spec,  "func": web_fetch }
}

def run_tool(tool_name: str, tool_args: dict, workspace: str = "") -> str:
    original_cwd = os.getcwd()
    if workspace:
        os.chdir(workspace)

    try:
        func = tool_registry[tool_name]["func"]
        result = func(**tool_args)

    except Exception:
        result = f"Error: tool error {tool_name}"

    os.chdir(original_cwd)
    return result