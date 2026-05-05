from ..infra.app_logging import log
from ..core.tool import Tool

class ReadFileTool(Tool):
    @staticmethod
    def spec():
        return {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read and return the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        }

    @staticmethod
    def call(file_path: str) -> str:
        log.info(f"read_file, file_path: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: file {file_path} does not exist"
        except Exception as e:
            log.error(f"Error reading file {file_path}: {e}")
            return f"Error reading file {file_path}: {e}"
