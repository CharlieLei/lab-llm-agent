import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOLS


load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL", "")

ENVIRONMENT_PROMPT = (
    "Windows: the bash tool runs through cmd.exe; "
    "use cmd.exe syntax, not Unix "
    "Bash or PowerShell syntax"
)
SYSTEM = (
    f"You are a coding agent at {os.getcwd()}. Environment: {ENVIRONMENT_PROMPT}. "
    "Before starting any multi-step task, use todo_write to plan your steps. "
    "Update status as you go."
)


client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

VALID_ROLES = {"system", "user", "assistant", "tool"}


def normalize_messages(messages):
    """Keep every message a valid chat role before sending it to the API."""
    normalized = []
    for msg in messages:
        msg = dict(msg)
        if msg.get("role") not in VALID_ROLES:
            print(f"\033[33m[WARN] invalid message role {msg.get('role')!r} -> 'user'\033[0m")
            msg["role"] = "user"
        if msg["role"] == "assistant" and msg.get("tool_calls") is None:
            msg.pop("tool_calls", None)
        normalized.append(msg)
    return normalized


def call_llm(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=normalize_messages(messages),
        tools=TOOLS,
        tool_choice="auto",
        parallel_tool_calls=True,
    )
    return response.choices[0].message
