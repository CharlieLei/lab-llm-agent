MARKERS = {
    "pending": "[ ]",
    "in_progress": "[>]",
    "completed": "[x]"
}

class TodoManager:
    def __init__(self) -> None:
        self.items : list[dict] = []
        self.round_since_todo = 0
        
    def run_todo_write(self, todos: list) -> str:
        print(f"\033[90m[TODO] {len(todos)} todos\033[0m")
        output = TODO.update(todos)
        return output
    
    def update(self, todos: list) -> str:
        
        # validated = []
        # in_progess_count = 0
        # for idx, todo in enumerate(todos):
        #     content = str(todo.get("content", "")).strip()
        #     status = str(todo.get("status", "pending")).lower()
        #     if status == "in_progress":
        #         in_progess_count += 1
        #     validated.append({"content": content, "status": status})
        # if in_progess_count > 1:
        #     raise ValueError("Only one todo can be in_progress at a time")
        
        self.items = todos
        return self.render()
    
    def render(self) -> str:
        if not self.items:
            return "No todos."
        
        done = sum(todo["status"] == "completed" for todo in self.items)
        lines = [f"{MARKERS[todo["status"]]} {todo["content"]}" for todo in self.items]
        lines.append(f"({done} / {len(self.items)} completed)")
        return "\n".join(lines)
    
    def record(self, used_todo: bool):
        self.round_since_todo = 0 if used_todo else self.round_since_todo + 1
    
    def remind(self) -> str | None:
        if self.round_since_todo >= 3:
            return "<reminder>Update your todos.</reminder>"
        return None
          

TODO = TodoManager()
