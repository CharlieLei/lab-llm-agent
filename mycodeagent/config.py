import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL", "")

WORKDIR = Path.cwd()

SKILLS_DIR = WORKDIR / "skills"

ENVIRONMENT_PROMPT = (
    "Windows: the bash tool runs through cmd.exe; "
    "use cmd.exe syntax, not Unix "
    "Bash or PowerShell syntax"
)
