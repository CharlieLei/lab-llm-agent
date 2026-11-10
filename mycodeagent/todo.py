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
        try:
            output = TODO.update(todos)
            print(f"\033[90m[TODO] {len(todos)} todos\033[0m")
            return output
        except ValueError as e:
            return f"Error: {e}"
    
    def update(self, todos: list) -> str:
        if not isinstance(todos, list):
            raise ValueError("todos must be a list")
        if len(todos) > 20:
            raise ValueError("Max 20 todos allowed.")
        
        validated = []
        for idx, todo in enumerate(todos):
            content = str(todo.get("content", "")).strip()
            if not content:
                raise ValueError(f"todos[{idx}] requires content.")

            status = str(todo.get("status", "pending")).lower()
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"todos[{idx}] has invalid status '{status}'")
            
            validated.append({"content": content, "status": status})
            
        in_progess_count = sum(1 for todo in validated if todo["status"] == "in_progress")
        if in_progess_count > 1:
            raise ValueError("Only one todo can be in_progress at a time")
        
        self.items = validated
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
