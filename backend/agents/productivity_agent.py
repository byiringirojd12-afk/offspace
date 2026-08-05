from .base_agent import BaseAgent


class ProductivityAgent(BaseAgent):
    name = "productivity"

    def run(self, task):
        return {"agent": self.name, "task": task, "status": "ready"}
