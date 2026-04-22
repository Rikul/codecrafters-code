import os

from .app_logging import log
from .helpers import trunc_str_with_ellipsis
from .tools.read_file import ReadFileTool
from .tools.write_file import WriteFileTool
from .tools.bash import BashTool
from .tools.web_fetch import WebFetchTool
from .tools.get_skills_dir import GetSkillsDirTool
from .tools.todo import TodoAddTool, TodoListTool, TodoClearTool, TodoUpdateTool


tool_registry = {
    "read_file": ReadFileTool,
    "write_file": WriteFileTool,
    "bash": BashTool,
    "web_fetch": WebFetchTool,
    "get_skills_dir": GetSkillsDirTool,
    "todo_add": TodoAddTool,
    "todo_list": TodoListTool,
    "todo_update": TodoUpdateTool,
    "todo_clear": TodoClearTool,
}

all_tool_specs = [tool.spec() for tool in tool_registry.values()]

MAX_TOOL_RESULT_LENGTH = 16000

def run_tool(tool_name: str, tool_args: dict) -> str:
    original_cwd = os.getcwd()
    
    try:
        func = tool_registry[tool_name].call
        result = func(**tool_args)
    except Exception as e:
        log.error(f"Error running tool {tool_name}: {str(e)}")
        result = f"Error running tool {tool_name}: {str(e)}"
    finally:
        os.chdir(original_cwd)
    
    return trunc_str_with_ellipsis(MAX_TOOL_RESULT_LENGTH, result)