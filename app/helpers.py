import os
from pathlib import Path
from app.display import log

def load_system_context() -> str:
    """
    Load files from the system.md directory and concatenate them into a single string.
    """

    system_context = ""
    system_md_files = [ "self.md", "user.md",  "workspace.md", "tool_instructions.md", "skills.md" ]
    system_context_dir = Path(__file__).parent / "system.md"

    for filename in system_md_files:
        if Path(os.path.join(system_context_dir, filename)).exists():

            try:
                with open(os.path.join(system_context_dir, filename), "r", encoding="utf-8") as f:
                    separator = "=" * 80
                    content = f.read().strip()
                    system_context += f'{separator}\n# {filename}\n{separator}\n\n{content}\n\n'

            except Exception as e:
                log.error(f"Error loading system context file {filename}: {e}")


    log.info(f"Loaded system context: {len(system_context)} characters")

    return system_context



def trunc_str_with_ellipsis(max_length : int, content: str) -> str:
    if len(content) > max_length:
        return content[:max_length-3] + "..."
    return content