from pathlib import Path

_APP_DIR = Path(__file__).parent

class Config:
    MODEL: str = "anthropic/claude-haiku-4.5"
    WORKSPACE_DIR: Path = _APP_DIR / "workspace"

    @staticmethod
    def get_model() -> str:
        return Config.MODEL
