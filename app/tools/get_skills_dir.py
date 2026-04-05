from ..app_logging import log
import pathlib


get_skills_dir_tool_spec = {
  "type": "function",
  "function": {
    "name": "get_skills_dir",
    "description": "Get the path to the skills directory"
  }
}

def get_skills_dir() -> str:
    log.info("get_skills_dir")

    skills_dir = pathlib.Path(__file__).parent.parent / "skills"
    return str(skills_dir.resolve())
