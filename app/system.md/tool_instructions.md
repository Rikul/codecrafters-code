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

## Todo Tool Guidelines

### When to Use Todo Tools

**✅ Use Todo Tools For:**
- **Long-running tasks** that span multiple steps
- **Complex projects** where progress needs tracking
- **Multi-phase work** with dependencies between steps
- **Large refactoring** where you need to track what's been done
- **Project planning** before diving into execution

**❌ Don't Use Todo Tools For:**
- Simple one-off commands
- Tasks that complete within a few tool calls
- When working memory alone is sufficient
- For tasks that should persist beyond the current session

### How to Use Todo Tools Effectively

1. **Plan First**: 
   - Use todos for complex tasks involving more than 3 steps
   - Use `todo_add` at the beginning of complex work
   - Break large tasks into 3-7 manageable subtasks
   - Add optional descriptions for clarity

2. **Track Progress**:
   - Update tasks to `in_progress` when you start working on them
   - Update to `done` when completed
   - Use `todo_list` periodically to check overall progress

3. **Clean Up**:
   - Use `todo_clear` when all work is complete
   - Clear before starting a new major project to avoid confusion

### Example Workflow

```
todo_add "Set up project structure", "Create directories and basic files"
todo_add "Implement core functionality", "Write main algorithm"
todo_add "Add tests", "Create unit tests for the new feature"
```

## Quality Checks
- Validate tool outputs before using them
- Verify file creation succeeded
- Check command exit codes

## Error Recovery
1. Identify the failure point
2. Check error messages for root cause
3. Try alternative approach if available
4. Inform user clearly if task cannot be completed
5. Suggest manual steps if automation fails