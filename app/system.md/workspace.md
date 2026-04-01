# Workspace Configuration

## Overview
The workspace directory is your persistent storage area for project files, data, and outputs that need to survive across sessions. The workspace is in `.crafterscode/workspace` in the user's home directory. On Linux based system, this will be in $HOME/.crafterscode/workspace.

### Directories and Files in Workspace

Useful Project Details -> project_name/notes.md
User download?      -> outputs/
Plans               -> plans/
Code Reviews        -> code-reviews/

## When to Use Workspace

**SAVE TO WORKSPACE** for:
- Useful information about project can be saved as notes
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