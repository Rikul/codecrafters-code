import os
from pathlib import Path
from .app_logging import log

def load_system_context() -> str:
    """
    Load sys_instructions.md and return its contents as the system context string.
    """
    sys_instructions_path = Path(__file__).parent / "sys_instructions.md"
    system_context = ""

    try:
        with open(sys_instructions_path, "r", encoding="utf-8") as f:
            system_context = f.read().strip()
    except Exception as e:
        log.error(f"Error loading system context: {e}")

    log.info(f"Loaded system context: {len(system_context)} characters")

    return system_context



def trunc_str_with_ellipsis(max_length : int, content: str) -> str:
    if len(content) > max_length:
        return content[:max_length-3] + "..."
    return content