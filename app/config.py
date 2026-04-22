from __future__ import annotations

import os
import tomllib
from pathlib import Path

_config : dict = {}

APP_NAME = "crafterscode"
PROJECT_HOME = Path.home() / f".{APP_NAME}"
HOME_CONFIG_PATH =  PROJECT_HOME / "config.toml"

def load(path: Path | str = HOME_CONFIG_PATH) -> None:
    global _config

    if not os.path.exists(path):
        raise RuntimeError(f"Config file {path} does not exist")

    with open(path, "rb") as f:
        _config = tomllib.load(f)

def get(key: str, default=None):
    return _config.get(key, default)

def __getattr__(name: str):
    if name in _config:
        return _config[name]
    raise AttributeError(f"Config has no attribute {name}")


def get_default_config() -> dict:

    default_config = """\
model = "deepseek/deepseek-v3.2"
max_iterations = 100
max_tokens = 32768
base_url = "https://openrouter.ai/api/v1"

[telegram]
BOT_TOKEN = ""
ALLOW_FROM = []  # List of allowed Telegram user IDs (integers). Must be non-empty.
"""

    return default_config
            