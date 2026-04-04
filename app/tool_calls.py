from .helpers import trunc_str_with_ellipsis

from .tools.read_file import read_file, read_file_tool_spec
from .tools.write_file import write_file, write_file_tool_spec
from .tools.bash import bash, bash_tool_spec
from .tools.web_fetch import web_fetch, web_fetch_tool_spec
from .tools.get_skills_dir import get_skills_dir, get_skills_dir_tool_spec
from .tools.todo import (
    todo_add, todo_add_tool_spec,
    todo_list, todo_list_tool_spec,
    todo_update, todo_update_tool_spec,
    todo_clear, todo_clear_tool_spec,
)
import os

tool_registry = {
    "read_file":    { "spec": read_file_tool_spec,  "func": read_file },
    "write_file":   { "spec": write_file_tool_spec, "func": write_file },
    "bash":         { "spec": bash_tool_spec,       "func": bash },
    "web_fetch":    { "spec": web_fetch_tool_spec,  "func": web_fetch },
    "get_skills_dir": { "spec": get_skills_dir_tool_spec, "func": get_skills_dir },
    "todo_add":    { "spec": todo_add_tool_spec,    "func": todo_add },
    "todo_list":   { "spec": todo_list_tool_spec,   "func": todo_list },
    "todo_update": { "spec": todo_update_tool_spec, "func": todo_update },
    "todo_clear":  { "spec": todo_clear_tool_spec,  "func": todo_clear },
}

MAX_TOOL_RESULT_LENGTH = 16000

def run_tool(tool_name: str, tool_args: dict) -> str:
    original_cwd = os.getcwd()
    
    try:
        func = tool_registry[tool_name]["func"]
        result = func(**tool_args)
    except Exception as e:
        result = f"Error running tool {tool_name}: {str(e)}"
    finally:
        os.chdir(original_cwd)
    
    return trunc_str_with_ellipsis(MAX_TOOL_RESULT_LENGTH, result)