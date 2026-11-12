import json
from config import WORKDIR, SKILLS_DIR, ENVIRONMENT_PROMPT
from llm import call_llm
from tools import BASE_TOOLS, BASE_HANDLERS, execute_tool
from hooks import trigger_hooks
from todo import TodoManager, TODO_WRITE_TOOL
from subagent import run_subagent, SPAWN_SUBAGENT_TOOL
from skill import SkillLoader, LOAD_SKILL_TOOL


TODO = TodoManager()

SKILL_LOADER = SkillLoader(SKILLS_DIR)

TOOLS = [*BASE_TOOLS, TODO_WRITE_TOOL, SPAWN_SUBAGENT_TOOL, LOAD_SKILL_TOOL]

TOOL_HANDLERS = {
    **BASE_HANDLERS,
    "todo_write": TODO.run_todo_write,
    "spawn_subagent": run_subagent,
    "load_skill": SKILL_LOADER.load
}

SYSTEM = (
    f"You are a coding agent at {WORKDIR}. Environment: {ENVIRONMENT_PROMPT}. "
    "Use tools to solve tasks. "
    "Act, don't explain.\n\n"
    f"Skills available:\n{SKILL_LOADER.catalog()}\n\n"
    "Use load_skill to read the full instructions when a skill applies."
)


def agent_loop(messages: list):
    loop_cnt = 0
    while True:
        loop_cnt += 1
        print(f"\033[90m[MAIN] loop {loop_cnt}.\033[0m")
        
        message = call_llm(TOOLS, messages)
        
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
            return
        
        used_todo = False
        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            if name == "todo_write":
                used_todo = True
            
            output = execute_tool(TOOL_HANDLERS, name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": output
            })
        
        remind = TODO.record(used_todo)
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
        except (EOFError, KeyboardInterrupt):
            break
        trigger_hooks("UserPromptSubmit", query)
        
        history.append({"role": "user", "content": query})
        
        agent_loop(history)
        
        message = history[-1]
        if message.get("content"):
            print(message["content"])
        print()

