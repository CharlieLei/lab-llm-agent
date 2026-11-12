import json
from config import WORKDIR, MODEL, ENVIRONMENT_PROMPT
from llm import call_llm
from tools import BASE_TOOLS, BASE_HANDLERS, execute_tool
from hooks import trigger_hooks


SUB_TOOLS = list(BASE_TOOLS)

SUB_HANDLERS = dict(BASE_HANDLERS)

SUB_SYSTEM = (
    f"You are a coding agent at {WORKDIR}. Environment: {ENVIRONMENT_PROMPT}. "
    "Complete the given task, then return a concise final answer."
)


def run_subagent(prompt: str) -> str:
    print("\n\033[35m[Subagent started]\033[0m")
    messages = [
        {"role": "system", "content": SUB_SYSTEM},
        {"role": "user", "content": prompt}
    ]
    
    for loop_cnt in range(30):
        print(f"\033[90m[SUBAGENT] loop {loop_cnt}.\033[0m")
        message = call_llm(SUB_TOOLS, messages)
        
        messages.append({
            "role": message.role, 
            "content": message.content, 
            "tool_calls": message.tool_calls
        })
        
        tool_calls = message.tool_calls
        if not tool_calls:
            force = trigger_hooks("Stop", messages)   # ← 退出之前
            if force:
                # hook 返回消息 → 注入消息并继续执行
                messages.append({"role": "user", "content": force})
                continue
            print("\033[35m[Subagent stopped]\033[0m\n")
            return message.content if message.content else "(no summary)"
        
        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            output = execute_tool(SUB_HANDLERS, name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": output
            })
        
    
    print("\033[35m[Subagent stopped]\033[0m\n")
    return "Subagent stopped after 30 turns without a final answer."  


SPAWN_SUBAGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "spawn_subagent",
        "description": "Run a subagent with fresh conversation context and return its final text.",
        "parameters": {
            "type": "object",
            "properties": {"prompt": {"type": "string", "minLength": 1}},
            "required": ["prompt"],
        },
    }
}
