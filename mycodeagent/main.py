import json
from typing import List
from llm import SYSTEM, call_llm
from tools import run_bash

        
def agent_loop(messages: List):
    message = call_llm(messages=messages)
    
    messages.append({"role": message.role, "content": message.content, "tool_calls": message.tool_calls})
    
    tool_calls = message.tool_calls
    if not tool_calls:
        return
    
    results = []
    for tool_call in tool_calls:
        arguments = json.loads(tool_call.function.arguments)
        print(f"\033[33m$ {arguments["command"]}\033[0m")
        output = run_bash(arguments["command"])
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": output
        })


if __name__ == "__main__":
    print("Enter a question, press Enter to send. Type q to quit.\n")
    
    history = [{"role": "system", "content": SYSTEM}]
    while True:
        query = input("\001\033[36m\002s01 >> \001\033[0m\002")
        history.append({"role": "user", "content": query})
        
        agent_loop(history)
        
        response_content = history[-1]["content"]
        print(response_content)

