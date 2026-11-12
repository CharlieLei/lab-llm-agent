from pathlib import Path
import yaml


class SkillLoader:
    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir
        self.skills: dict[str, dict[str, str]] = {}
        self.scan()
    
    def scan(self):
        for manifest in sorted(self.skills_dir.glob("*/SKILL.md")):
            content = manifest.read_text(encoding="utf-8")
            frontmatter = content.split("---", 2)[1]
            metadata = yaml.safe_load(frontmatter)
            
            self.skills[metadata["name"]] = {
                "name": metadata["name"],
                "description": metadata["description"],
                "content": content
            }
    
    def catalog(self) -> str:
        if not self.skills:
            return "(no skills found)"
        return "\n".join(
            f"- {skill["name"]}: {skill["description"]}"
            for skill in self.skills.values()
        )
    
    def load(self, name: str) -> str:
        skill = self.skills.get(name)
        if not skill:
            available = ", ".join(self.skills) or "none"
            return f"Error: Unknown skill '{name}'. Available: {available}"
        return skill["content"]


LOAD_SKILL_TOOL = {
    "type": "function",
    "function": {
        "name": "load_skill",
        "description": "Load the full instructions of a skill by name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Skill name, exactly as listed in the catalog."
                }
            },
            "required": ["name"]
        }
    }
}
