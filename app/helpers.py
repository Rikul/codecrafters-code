import os
import sys
from pathlib import Path

def load_system_context() -> str:
    """
    Load files from the system.md directory and concatenate them into a single string.
    """

    system_context = ""
    system_md_files = [ "self.md", "user.md",  "workspace.md", "tool_instructions.md" ]
    system_context_dir = Path(__file__).parent / "system.md"

    for filename in system_md_files:
        if Path(os.path.join(system_context_dir, filename)).exists():

            try:
                with open(os.path.join(system_context_dir, filename), "r", encoding="utf-8") as f:
                    separator = "=" * 80
                    content = f.read().strip()
                    system_context += f'{separator}\n# {filename}\n{separator}\n\n{content}\n\n'

            except Exception as e:
                print(f"Error loading system context file {filename}: {e}")


    print(f"Loaded system context: {len(system_context)} lines\n{system_context[:1000]}...\n", file=sys.stderr)

    return system_context
