import os
import subprocess


TOOLS = [{
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a shell command.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"}
            },
            "required": ["command"],
        }
    }
}]


def run_bash(command: str) -> str:
    r = subprocess.run(
        command,
        shell=True,
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
        errors="replace",
        timeout=120
    )
    out = (r.stdout + r.stderr).strip()
    return out[:50000] if out else "(no output)"
