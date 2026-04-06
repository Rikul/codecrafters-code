from abc import ABC, abstractmethod
from typing import Any

class Tool(ABC):
    @staticmethod
    @abstractmethod
    def call(args: Any) -> Any:
        pass

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @staticmethod
    @abstractmethod
    def description() -> str:
        pass

    @staticmethod
    @abstractmethod
    def spec() -> dict:
        pass