from __future__ import annotations

import logging
from enum import StrEnum

class ANSI(StrEnum):
    RESET  = "\033[0m"
    DIM    = "\033[2m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    CYAN   = "\033[36m"
    BOLD   = "\033[1m"
    BOLD_RED = "\033[1;31m"


class AnsiFormatter(logging.Formatter):
    LEVELS = {
        logging.DEBUG:    f"{ANSI.DIM}DEBUG{ANSI.RESET}",
        logging.INFO:     f"{ANSI.GREEN}INFO{ANSI.RESET}",
        logging.WARNING:  f"{ANSI.YELLOW}WARN{ANSI.RESET}",
        logging.ERROR:    f"{ANSI.RED}ERROR{ANSI.RESET}",
        logging.CRITICAL: f"{ANSI.BOLD_RED}CRIT{ANSI.RESET}",
    }

    def format(self, record: logging.LogRecord) -> str:
        level = self.LEVELS.get(record.levelno, record.levelname)
        msg = record.getMessage()
        return f"{ANSI.DIM}{self.formatTime(record, '%H:%M:%S')}{ANSI.RESET} {level}" \
               f" {ANSI.DIM}{record.name} {msg}{ANSI.RESET}"


handler = logging.StreamHandler()
handler.setFormatter(AnsiFormatter())

logging.basicConfig(level=logging.INFO, handlers=[handler])

log = logging.getLogger(__name__)

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
