import os

from .app_logging import log
from .helpers import trunc_str_with_ellipsis
from .tools.read_file import ReadFileTool
from .tools.write_file import WriteFileTool
from .tools.bash import BashTool
from .tools.web_fetch import WebFetchTool
from .tools.get_skills_dir import GetSkillsDirTool
from .tools.todo import TodoAddTool, TodoListTool, TodoClearTool, TodoUpdateTool
from .tools.calculator import CalculatorTool
from .tools.hackernews import HackerNewsTool

from .tools.web_search import WebSearchText
from .tools.web_search import WebSearchImages
from .tools.web_search import WebSearchVideos
from .tools.web_search import WebSearchNews
from .tools.web_search import WebSearchBooks

from .tools.sched_tasks_tool import ListScheduledTasks, AddScheduledTask, DisableScheduledTask, \
                        RemoveScheduledTask, GetScheduledTaskOutput, EnableScheduledTask

import json

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
    
    "calculator": CalculatorTool,
    "hackernews": HackerNewsTool,

    "websearch_text": WebSearchText,
    "websearch_images": WebSearchImages,
    "websearch_videos": WebSearchVideos,
    "websearch_news": WebSearchNews,
    "websearch_books": WebSearchBooks,

    "list_scheduled_tasks": ListScheduledTasks,
    "add_scheduled_task": AddScheduledTask,
    "disable_scheduled_task": DisableScheduledTask,
    "enable_scheduled_task": EnableScheduledTask,
    "remove_scheduled_task": RemoveScheduledTask,
    "get_scheduled_task_output": GetScheduledTaskOutput
}

all_tool_specs = [tool.spec() for tool in tool_registry.values()]

_SCHED_TOOLS = {"list_scheduled_tasks", "add_scheduled_task", "enable_scheduled_task",
                "disable_scheduled_task", "remove_scheduled_task", "get_scheduled_task_output"}
helper_tool_specs = [tool.spec() for k, tool in tool_registry.items() if k not in _SCHED_TOOLS]

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
    
    if not isinstance(result, str):
        result = json.dumps(result)
    
    return trunc_str_with_ellipsis(MAX_TOOL_RESULT_LENGTH, result)
    