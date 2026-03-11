

class Config:
    MODEL: str = "anthropic/claude-haiku-4.5"

    @staticmethod
    def get_model() -> str:
        return Config.MODEL
