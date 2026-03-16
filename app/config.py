import os
from pathlib import Path

HOME_DIR: Path = Path.home()
APP_DIR: Path = Path(__file__).parent

class Config:

    @staticmethod
    def get_model() -> str:
        model = os.environ.get("LLM_MODEL")
        if not model:
            raise RuntimeError("LLM_MODEL is not set")
        
        return model
