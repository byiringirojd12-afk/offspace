from typing import Any, Dict, List


class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.history: List[Dict[str, Any]] = []

    def respond(self, task: str) -> str:
        response = f"{self.name} ({self.role}) reviewing task: {task}"
        self.history.append({"task": task, "response": response})
        return response


class AgentManager:
    def __init__(self):
        self.agents: Dict[str, Agent] = {
            "coding": Agent("Coding Agent", "software development"),
            "research": Agent("Research Agent", "information retrieval"),
            "productivity": Agent("Productivity Agent", "workflow coordination"),
        }

    def delegate(self, task: str) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for key, agent in self.agents.items():
            results[key] = agent.respond(task)
        return results

    def get_agent(self, name: str) -> Agent:
        return self.agents[name]
