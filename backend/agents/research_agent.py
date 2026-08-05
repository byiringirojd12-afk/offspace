from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    name = "research"

    def run(self, task):
        return {"agent": self.name, "task": task, "status": "ready"}
