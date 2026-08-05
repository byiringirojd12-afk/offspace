"""Agent selection system for Offspace."""


class AgentSelector:
    def select(self, reasoning_result):
        mapping = {
            "coding": "CodingAgent",
            "research": "ResearchAgent",
            "productivity": "ProductivityAgent",
            "trading": "TradingAgent",
            "general": "GeneralAgent",
        }

        intent = reasoning_result.get("intent", "general")
        return mapping.get(intent, "GeneralAgent")
