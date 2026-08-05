class AgentOrchestrator:
    """Coordinate agents and select execution flow."""

    def __init__(self):
        self.agents = {}

    def register(self, name, agent):
        self.agents[name] = agent

    def dispatch(self, task_type, task):
        agent = self.agents.get(task_type)
        if not agent:
            return {"error": "No agent available"}
        return agent.run(task)
