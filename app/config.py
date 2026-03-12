import os
from pathlib import Path
from dotenv import load_dotenv

_APP_DIR = Path(__file__).parent
HOME_DIR: Path = Path.home()

class Config:
    WORKSPACE_DIR: Path = HOME_DIR / "workspace"

    @staticmethod
    def get_model() -> str:
        load_dotenv()
        model = os.getenv("LLM_MODEL")
        if not model:
            raise RuntimeError("LLM_MODEL is not set")
        
        return model
