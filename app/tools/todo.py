from app.display import log

_tasks: dict[str, dict] = {}
_next_id = 1

_VALID_STATUSES = {"todo", "in_progress", "done"}

todo_add_tool_spec = {
    "type": "function",
    "function": {
        "name": "todo_add",
        "description": "Add a new task to the todo list",
        "parameters": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short title for the task"
                },
                "description": {
                    "type": "string",
                    "description": "Optional longer description of the task"
                }
            }
        }
    }
}

todo_list_tool_spec = {
    "type": "function",
    "function": {
        "name": "todo_list",
        "description": "List all tasks and their statuses"
    }
}

todo_clear_tool_spec = {
    "type": "function",
    "function": {
        "name": "todo_clear",
        "description": "Todos are done, clear all todos"
    }
}

todo_update_tool_spec = {
    "type": "function",
    "function": {
        "name": "todo_update",
        "description": "Update the status of a task",
        "parameters": {
            "type": "object",
            "required": ["task_id", "status"],
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID of the task to update"
                },
                "status": {
                    "type": "string",
                    "enum": ["todo", "in_progress", "done"],
                    "description": "New status for the task"
                }
            }
        }
    }
}


def todo_add(title: str, description: str = "") -> str:
    global _next_id
    log.info(f"todo_add, title: {title}")

    task_id = str(_next_id)
    _next_id += 1
    _tasks[task_id] = {"title": title, "description": description, "status": "todo"}
    return f"Task {task_id} added: {title}"


def todo_list() -> str:
    log.info("todo_list")

    if not _tasks:
        return "No tasks."

    lines = []
    for task_id, task in _tasks.items():
        line = f"[{task_id}] [{task['status']}] {task['title']}"
        if task["description"]:
            line += f" — {task['description']}"
        lines.append(line)
    return "\n".join(lines)


def todo_clear() -> str:
    global _next_id
    log.info("todo_clear")
    count = len(_tasks)
    _tasks.clear()
    _next_id = 1
    return f"Cleared {count} task(s)."


def todo_update(task_id: str, status: str) -> str:
    log.info(f"todo_update, task_id: {task_id}, status: {status}")

    if task_id not in _tasks:
        return f"Error: task {task_id} not found"

    if status not in _VALID_STATUSES:
        return f"Error: invalid status '{status}'. Must be one of: {', '.join(sorted(_VALID_STATUSES))}"

    _tasks[task_id]["status"] = status
    return f"Task {task_id} updated to '{status}'"
