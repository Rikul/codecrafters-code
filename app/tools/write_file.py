import os
import sys

def write_file(file_path: str, content: str) -> str:
    print(f"func: write_file, file_path: {file_path}", file=sys.stderr)

    with open(file_path, "w", encoding = "utf-8") as f:
        f.write(content)
    
    return f"Successfully wrote to file {file_path}"