import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL", "")

WORKDIR = Path.cwd()

ENVIRONMENT_PROMPT = (
    "Windows: the bash tool runs through cmd.exe; "
    "use cmd.exe syntax, not Unix "
    "Bash or PowerShell syntax"
)


client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
