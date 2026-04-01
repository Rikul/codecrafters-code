from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "crafterscode"

def ensure_home_dir() -> None:
    import os
    from pathlib import Path

    # Create app home directory in user's home if it doesn't exist
    home_dir = Path.home() / f".{APP_NAME}"
    if not home_dir.exists():
        home_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(home_dir, 0o700)
        print(f"Created home directory: {home_dir}")

    # Create workspace, skills, logs directories
    for subdir in ["workspace"]:
        subdir_path = home_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created {subdir} directory: {subdir_path}")
    
    # Copy config.toml from current directory to home directory if it doesn't exist
    config_path = home_dir / "config.toml"
    if not config_path.exists():
        current_config_path = Path(__file__).parent / "config.toml"
        if current_config_path.exists():
            with open(current_config_path, "r", encoding="utf-8") as src, open(config_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            print(f"Copied config.toml to home directory: {config_path}")
        else:
            default_config = """model = "deepseek/deepseek-v3.2\n""" \
                             """max_iterations = 100\n""" \
                             """max_tokens = 32768\n"""
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(default_config)
            print(f"Created default config.toml in home directory: {config_path}")
