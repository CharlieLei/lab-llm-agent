import json
from typing import List
from llm import SYSTEM, call_llm
from tools import TOOL_HANDLERS
from permission import check_permission

        
def agent_loop(messages: List):
    while True:
        message = call_llm(messages=messages)
        
        messages.append({"role": message.role, "content": message.content, "tool_calls": message.tool_calls})
        
        tool_calls = message.tool_calls
        if not tool_calls:
            return
        
        for tool_call in tool_calls:
            func = tool_call.function
            name = func.name
            args = json.loads(func.arguments)
            print(f"\033[33m> {func.name}\033[0m")
            
            if not check_permission(name, args):
                print(f"\033[31m< Permission denied.\033[0m")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "Permission denied."
                })
                continue
            
            handler = TOOL_HANDLERS[func.name]
            output = handler(**args) if handler else f"Unknown: {func.name}"
            print(f"\033[32m< {str(output)[:200]}\033[0m")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": output
            }) 


if __name__ == "__main__":
    print("Enter a question, press Enter to send. \n")
    
    history = [{"role": "system", "content": SYSTEM}]
    while True:
        try:
            query = input("\001\033[36m\002q >> \001\033[0m\002")
        except EOFError, KeyboardInterrupt:
            break
        
        history.append({"role": "user", "content": query})
        
        agent_loop(history)
        
        message = history[-1]
        if message.get("content"):
            print(message["content"])
        print()

