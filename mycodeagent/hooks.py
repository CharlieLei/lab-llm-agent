from llm import WORKDIR
from permission import permission_hook


HOOKS = {
    "UserPromptSubmit": [],
    "PreToolUse": [],
    "PostToolUse": [],
    "Stop": [],
}


def register_hook(event: str, callback):
    HOOKS[event].append(callback)

def trigger_hooks(event: str, *args):
    for callback in HOOKS[event]:
        result = callback(*args)
        if result is not None:   # 返回值 ≠ None → hook 说"停"
            return result
    return None

###########################################


def context_inject_hook(query: str) -> str | None:
    """Inject current working directory info into every prompt."""
    print(f"\033[90m[HOOK] UserPromptSubmit: working in {WORKDIR}\033[0m")
    return None   # return None = 不修改提示词，直接放行


def log_hook(tool_name, args):
    """PreToolUse: log every tool call."""
    args_preview = str(list(args.values())[:2])
    if len(args_preview) > 60:
        args_preview = args_preview[:60] + " ...(more)"
    print(f"\033[33m> {tool_name} {args_preview}\033[0m")
    return None


def print_output_hook(tool_name, output):
    if len(output) > 60:
        output = output[:200] + "   ...(more)"
    print(f"\033[32m< {str(output)}\033[0m")


def large_output_hook(tool_name, output):
    """PostToolUse: warn on large output."""
    if len(str(output)) > 100000:
        print(f"\033[33m[HOOK] Large output from {tool_name}: {len(str(output))} chars\033[0m")
    return None


def summary_hook(messages: list):
    tool_count = sum(1 for m in messages if m.get("role") == "tool")
    print(f"\033[90m[HOOK] Stop: session used {tool_count} tool calls\033[0m")
    return None


register_hook("UserPromptSubmit", context_inject_hook)
register_hook("PreToolUse", permission_hook)
register_hook("PreToolUse", log_hook)
register_hook("PostToolUse", print_output_hook)
register_hook("PostToolUse", large_output_hook)
register_hook("Stop", summary_hook)
