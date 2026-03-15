# Workspace Configuration

## Overview
The workspace directory is your persistent storage area for project files, data, and outputs that need to survive across sessions.

## How to Use Workspace

### File Location Decision Tree

One-time task? → /tmp/
Reusable across projects? → scripts/ or templates/
New app or project? → projects/{project-name}/
User download? → outputs/
Plans -> plans/
Code Reviews -> code-reviews/

### Quick Examples

- If the user wants you to create a game called `sudoku1`. Create a `sudoku1` dir in `projects` directory.
- If the user wants to create a reusable utility, use the `scripts` directory.
- Code reviews would go in `code-reviews` directory, etc.
- Plans would go in `plans` directory, with appropriate naming conventions.

### Critical Rules

1. **ALWAYS use `mkdir -p`** - never assume directories exist
2. **Work in /tmp/**
3. **Use absolute paths** 
4. **Create README.md** for new projects

## When to Use Workspace

✅ **SAVE TO WORKSPACE** for:
- Project files that will be referenced later
- Reusable scripts and utilities
- Final deliverables that user wants to keep
- Data that needs to persist across sessions
- Configuration files
- Documentation and knowledge base
- Templates for recurring tasks

## Best Practices

### Organization
1. **Use descriptive names**: `customer-analysis-2024` not `proj1`
2. **Group related files**: Keep project files together
3. **Separate concerns**: Code in src/, data in data/, docs in docs/
4. **Version important files**: Use timestamps or version numbers
5. **Document structure**: Include README.md in project folders
