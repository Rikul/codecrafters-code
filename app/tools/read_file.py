import os
import sys


def read_file(file_path: str) -> str:
    #file_path = os.path.abspath(file_path)

    print(f"func: read_file, file_path: {file_path}", file=sys.stderr)

    if not os.path.exists(file_path):
        return f"Error: file {file_path} does not exist"
    
    with open(file_path, encoding = "utf-8") as f:
        return f.read()
