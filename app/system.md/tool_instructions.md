# Tool Usage Instructions

Guidelines for when and how to use available tools effectively.

## Available Tools

- **bash**: Execute shell commands
- **read_file**: Read existing files
- **write_file**: Create or overwrite files
- **web_fetch**: Retrieve content from specific URLs
- **todo_add**: Add a task to the todo list (`title`, optional `description`)
- **todo_list**: List all tasks and their statuses
- **todo_update**: Update a task's status (`task_id`, `status`: `todo` | `in_progress` | `done`)
- **todo_clear**: Clear all todos when the work is complete

### Quality Checks
- Validate tool outputs before using them
- Verify file creation succeeded
- Check command exit codes
- Confirm URLs are accessible before fetching

### Error Recovery
1. Identify the failure point
2. Check error messages for root cause
3. Try alternative approach if available
4. Inform user clearly if task cannot be completed
5. Suggest manual steps if automation fails