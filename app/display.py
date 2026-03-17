import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Confirm

console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console)]
)

log = logging.getLogger("rich")

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def ask_permission(tool_name: str, args: dict) -> bool:
    console.print(f"[bold yellow]⚡ Tool Call[/bold yellow]: [cyan]{tool_name}[/cyan]   Args: {args}")
    return Confirm.ask("Proceed?", default=True)