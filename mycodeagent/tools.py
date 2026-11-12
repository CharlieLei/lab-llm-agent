import os
from pathlib import Path
import subprocess
from config import WORKDIR
from hooks import trigger_hooks


def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
            return "Error: Dangerous command blocked"
    try:
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
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


def run_read(path: str, limit: int | None = None) -> str:
    try:
        lines = safe_path(path).read_text(encoding="utf-8").splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    try:
        file_path = safe_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        file_path = safe_path(path)
        text = file_path.read_text(encoding="utf-8")
        if old_text not in text:
            return f"Error: text not found in {path}"
        file_path.write_text(text.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


def run_glob(pattern: str) -> str:
    import glob as g
    try:
        matches = sorted({
            match for match in g.glob(
                pattern, root_dir=WORKDIR, recursive=True)
            if (WORKDIR / match).resolve().is_relative_to(WORKDIR)
        })
        shown = matches[:200]
        if len(matches) > 200:
            shown.append("... (more matches omitted; narrow the pattern)")
        return "\n".join(shown) if shown else "(no matches)"
    except Exception as e:
        return f"Error: {e}"



BASH_TOOL = {
  "type": "function",
  "function": {
    "name": "bash",
    "description": "Run a shell command.",
    "parameters": {
      "type": "object",
      "properties": {
        "command": { "type": "string" }
      },
      "required": ["command"]
    }
  }
}

READ_FILE_TOOL = {
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Read file contents.",
    "parameters": {
      "type": "object",
      "properties": {
        "path": { "type": "string" },
        "limit": { "type": "integer" }
      },
      "required": ["path"]
    }
  }
}

WRITE_FILE_TOOL = {
  "type": "function",
  "function": {
    "name": "write_file",
    "description": "Write content to a file.",
    "parameters": {
      "type": "object",
      "properties": {
        "path": { "type": "string" },
        "content": { "type": "string" }
      },
      "required": ["path", "content"]
    }
  }
}

EDIT_FILE_TOOL = {
  "type": "function",
  "function": {
    "name": "edit_file",
    "description": "Replace exact text in a file once.",
    "parameters": {
      "type": "object",
      "properties": {
        "path": { "type": "string" },
        "old_text": { "type": "string" },
        "new_text": { "type": "string" }
      },
      "required": ["path", "old_text", "new_text"]
    }
  }
}

GLOB_TOOL = {
  "type": "function",
  "function": {
    "name": "glob",
    "description": "Find files matching a glob pattern; ** matches recursively.",
    "parameters": {
      "type": "object",
      "properties": {
        "pattern": { "type": "string" }
      },
      "required": ["pattern"]
    }
  }
}

BASE_TOOLS = [
    BASH_TOOL,
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    EDIT_FILE_TOOL,
    GLOB_TOOL,
]

BASE_HANDLERS = {
    "bash": run_bash, 
    "read_file": run_read, 
    "write_file": run_write,
    "edit_file": run_edit, 
    "glob": run_glob
}


def execute_tool(handlers, tool_name, args):
    blocked = trigger_hooks("PreToolUse", tool_name, args)
    if blocked:
        print(f"\033[31m< Tool blocked: {blocked}\033[0m")
        return blocked
    
    handler = handlers[tool_name]
    output = handler(**args) if handler else f"Unknown: {tool_name}"
    
    trigger_hooks("PostToolUse", tool_name, output)
    return output
