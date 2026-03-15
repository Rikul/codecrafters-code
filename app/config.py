import os
from pathlib import Path
from dotenv import load_dotenv

HOME_DIR: Path = Path.home()
APP_DIR: Path = Path(__file__).parent

class Config:

    @staticmethod
    def get_model() -> str:
        load_dotenv()
        model = os.getenv("LLM_MODEL")
        if not model:
            raise RuntimeError("LLM_MODEL is not set")
        
        return model
