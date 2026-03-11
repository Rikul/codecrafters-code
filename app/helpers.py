import os
from pathlib import Path

def load_system_context() -> str:
    """
    Load files from the system.md directory and concatenate them into a single string.
    """

    system_context = ""
    system_md_files = [ "self.md", "user.md", "tool_instructions.md"]
    system_context_dir = Path(__file__).parent / "system.md"

    for filename in system_md_files:
        if Path(os.path.join(system_context_dir, filename)).exists():
            try:
                with open(os.path.join(system_context_dir, filename), "r", encoding="utf-8") as f:
                    system_context += f"---\n# {filename} \n\n" + f.read() + "\n"
            except Exception as e:
                print(f"Error loading system context file {filename}: {e}")

    return system_context