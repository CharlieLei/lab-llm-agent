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
    "Use bash to solve tasks. Act, don't explain."
)


client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def call_llm(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        parallel_tool_calls=True,
    )
    return response.choices[0].message
