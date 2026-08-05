from .base_agent import BaseAgent


class CodingAgent(BaseAgent):
    name = "coding"

    def run(self, task):
        return {"agent": self.name, "task": task, "status": "ready"}
