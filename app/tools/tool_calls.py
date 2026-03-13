from app.tools.read_file import read_file, read_file_tool_spec
from app.tools.write_file import write_file, write_file_tool_spec
from app.tools.bash import bash, bash_tool_spec
from app.tools.web_fetch import web_fetch, web_fetch_tool_spec

tool_registry = {
    "read_file":    { "spec": read_file_tool_spec,  "func": read_file },
    "write_file":   { "spec": write_file_tool_spec, "func": write_file },
    "bash":         { "spec": bash_tool_spec,       "func": bash },
    "web_fetch":    { "spec": web_fetch_tool_spec,  "func": web_fetch }
}

def run_tool(tool_name: str, tool_args: dict) -> str:

    try:
        func = tool_registry[tool_name]["func"]
        return func(**tool_args)

    except Exception:
        return f"Error: tool error {tool_name}"
