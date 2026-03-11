import os
import subprocess
import sys

def bash(command: str) -> str:
    print(f"func: bash, command: {command}", file=sys.stderr)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr}"

    except Exception as e:
        return f"Error executing command: {e}"
