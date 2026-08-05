from .base_agent import BaseAgent


class TradingAgent(BaseAgent):
    name = "trading"

    def run(self, task):
        return {"agent": self.name, "task": task, "status": "ready"}
