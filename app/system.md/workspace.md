# Workspace Configuration

## Overview
The workspace directory is your persistent storage area for project files, data, and outputs that need to survive across sessions.

## How to Use Workspace

### File Location Decision Tree

One-time task? → /tmp/
Reusable across projects? → scripts/ or templates/
Project-specific? → projects/{project-name}/
User download? → outputs/
Skills? -> skills/
Plans -> plans/
Code Reviews -> code-reviews/


### Quick Examples

- If the user wants you to create a game called `sudoku1`. Create a `sudoku1` dir in `projects` directory.
- If the user wants to create a reusable utility, use the `scripts` directory.
- For a new skill, use the `skills` directory.
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


## Path References

### Absolute Paths (Recommended)
```python
import os

# Get workspace root
WORKSPACE_ROOT = os.path.join(os.getcwd(), 'workspace')

# Access subdirectories
PROJECTS_DIR = os.path.join(WORKSPACE_ROOT, 'projects')
DATA_DIR = os.path.join(WORKSPACE_ROOT, 'data')
SCRIPTS_DIR = os.path.join(WORKSPACE_ROOT, 'scripts')
```

### Relative Paths
```bash
./workspace/projects/my-project/

cd workspace
./projects/my-project/
```

## Best Practices

### Organization
1. **Use descriptive names**: `customer-analysis-2024` not `proj1`
2. **Group related files**: Keep project files together
3. **Separate concerns**: Code in src/, data in data/, docs in docs/
4. **Version important files**: Use timestamps or version numbers

### Cleanup
1. **Archive completed projects**: Move to `workspace/archive/`
2. **Clean temporary data**: Remove outdated cache files
3. **Document structure**: Include README.md in project folders

### Documentation
```bash
# Each project should have:
workspace/projects/my-project/
├── README.md           # Project overview
├── CHANGELOG.md        # Version history
└── requirements.txt    # Dependencies
```

## Examples

### Example 1: Shared Utility Library
```bash
# Create utility module
mkdir -p workspace/scripts/python/utils
cat > workspace/scripts/python/utils/data_helpers.py << 'EOF'
def clean_dataframe(df):
    """Common data cleaning operations"""
    # implementation
    return df
EOF

# Use in any project
python -c "
import sys
sys.path.append('workspace/scripts/python')
from utils.data_helpers import clean_dataframe
# use the function
"
```

### Example 2: Template System
```bash
# Store templates
mkdir -p workspace/templates/reports

# Create template
cat > workspace/templates/reports/analysis_template.md << 'EOF'
# Analysis Report

## Executive Summary
[Summary here]

## Methodology
[Methods here]

## Results
[Results here]
EOF

# Use template in new project
cp workspace/templates/reports/analysis_template.md \
   workspace/projects/new-analysis/report.md
```

## Environment Variables

You can set these for easier access:
```bash
export WORKSPACE_ROOT="$(pwd)/workspace"
export WORKSPACE_PROJECTS="$WORKSPACE_ROOT/projects"
export WORKSPACE_DATA="$WORKSPACE_ROOT/data"
export WORKSPACE_SCRIPTS="$WORKSPACE_ROOT/scripts"
```

## Querying Workspace Contents

### List Projects
```bash
ls -la workspace/projects/
```

### Find Files
```bash
# Find all Python scripts
find workspace/scripts -name "*.py"

# Find large data files
find workspace/data -type f -size +10M

# Find recent files
find workspace -type f -mtime -7  # modified in last 7 days
```

### Search Content
```bash
# Search for keyword in all files
grep -r "search_term" workspace/

# Search specific file types
grep -r "function_name" workspace/scripts/ --include="*.py"
```

## Access Control & Privacy

- **User-specific**: Each user has their own workspace
- **Session persistence**: Files remain between sessions
- **No cross-user access**: Cannot access other users' workspaces
- **Backup recommendation**: Important files should be downloaded/backed up

## Troubleshooting

### Issue: Workspace not found
```bash
# Initialize workspace
mkdir -p workspace/{projects,data,outputs,scripts,templates,knowledge,config}
```

### Issue: Permission denied
```bash
# Check permissions
ls -la workspace/

# Fix permissions if needed
chmod -R u+rw workspace/
```

### Issue: Path confusion
```bash
# Always verify current directory
pwd

# List full path
realpath workspace/
```

## Quick Reference Card
```bash
# Create project structure
mkdir -p workspace/projects/PROJECT_NAME/{src,data,docs,tests}

# Work in temp directory
cd /tmp/ && # do work here

# Save to workspace
cp /tmp/OUTPUT_FILE workspace/projects/PROJECT_NAME/

```