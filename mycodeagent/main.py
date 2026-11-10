import json
from typing import List
from llm import SYSTEM, call_llm
from tools import TOOL_HANDLERS
from hooks import trigger_hooks
from todo import TODO

        
def agent_loop(messages: List):
    while True:
        print("\033[31m[LOOP] start.\033[0m")
        message = call_llm(messages=messages)
        
        messages.append({"role": message.role, "content": message.content, "tool_calls": message.tool_calls})
        
        tool_calls = message.tool_calls
        if not tool_calls:
            force = trigger_hooks("Stop", messages)   # ← 退出之前
            if force:
                # hook 返回消息 → 注入消息并继续执行
                messages.append({"role": "user", "content": force})
                continue
            return
        
        used_todo = False
        for tool_call in tool_calls:
            func = tool_call.function
            name = func.name
            args = json.loads(func.arguments)
            print(f"\033[33m> {func.name}\033[0m")
            
            if name == "todo_write":
                used_todo = True
            
            blocked = trigger_hooks("PreToolUse", name, args)
            if blocked:
                print(f"\033[31m< Tool blocked: {blocked}\033[0m")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "Permission denied."
                })
                continue
            
            handler = TOOL_HANDLERS[func.name]
            output = handler(**args) if handler else f"Unknown: {func.name}"
            print(f"\033[32m< {str(output)[:200]}\033[0m")
            
            trigger_hooks("PostToolUse", name, output)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": output
            })
        
        TODO.record(used_todo)
        remind = TODO.remind()
        if remind:
            messages.append({
                "role": "user",
                "content": remind
            })


if __name__ == "__main__":
    print("Enter a question, press Enter to send. \n")
    
    history = [{"role": "system", "content": SYSTEM}]
    while True:
        try:
            query = input("\001\033[36m\002q >> \001\033[0m\002")
        except EOFError, KeyboardInterrupt:
            break
        trigger_hooks("UserPromptSubmit", query)
        
        history.append({"role": "user", "content": query})
        
        agent_loop(history)
        
        message = history[-1]
        if message.get("content"):
            print(message["content"])
        print()

