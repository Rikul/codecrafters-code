from __future__ import annotations

import os
import tomllib
from pathlib import Path

_config : dict = {}

def load(path: Path | str = "") -> None:
    global _config

    if not path:
        path = Path(__file__).parent / "config.toml"

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
