from __future__ import annotations

import logging

from rich.prompt import Confirm

RESET  = "\033[0m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
CYAN   = "\033[36m"

class AnsiFormatter(logging.Formatter):
    LEVELS = {
        logging.DEBUG:    f"{DIM}DEBUG{RESET}",
        logging.INFO:     f"{GREEN}INFO{RESET}",
        logging.WARNING:  f"{YELLOW}WARN{RESET}",
        logging.ERROR:    f"{RED}ERROR{RESET}",
        logging.CRITICAL: f"{RED}\033[1mCRIT{RESET}",
    }

    def format(self, record: logging.LogRecord) -> str:
        level = self.LEVELS.get(record.levelno, record.levelname)
        msg = record.getMessage()
        return f"{DIM}{self.formatTime(record, '%H:%M:%S')}{RESET} {level} {DIM}{record.name} {msg}{RESET}"


handler = logging.StreamHandler()
handler.setFormatter(AnsiFormatter())

logging.basicConfig(level=logging.INFO, handlers=[handler])

log = logging.getLogger(__name__)

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def ask_permission(tool_name: str, args: dict) -> bool:
    print(f"{YELLOW}⚡ Tool Call{RESET}: {CYAN}{tool_name}{RESET}   Args: {args}")
    answer = input(f"Proceed? {DIM}[Y/n]{RESET} ").strip().lower()
    return answer in ("", "y", "yes")