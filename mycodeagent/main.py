import json
from typing import List
from llm import WORKDIR, MODEL, ENVIRONMENT_PROMPT, client
from tools import TOOLS, TOOL_HANDLERS
from hooks import trigger_hooks
from todo import TODO


SYSTEM = (
    f"You are a coding agent at {WORKDIR}. Environment: {ENVIRONMENT_PROMPT}. "
    "Before starting any multi-step task, use todo_write to plan your steps. "
    "Update status as you go."
)


def call_llm(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        parallel_tool_calls=True,
    )
    return response.choices[0].message


def agent_loop(messages: List):
    loop_cnt = 0
    while True:
        loop_cnt += 1
        print(f"\033[90m[MAIN] loop {loop_cnt}.\033[0m")
        
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
            
            trigger_hooks("PostToolUse", name, output)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": output
            })
        
        TODO.record(used_todo)
        remind = TODO.remind()
        if remind:
            print(f"\033[31m< Todo reminded.\033[0m")
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

