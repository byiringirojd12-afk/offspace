"""Reasoning engine foundation for Offspace.

Responsible for analyzing requests and selecting execution strategies.
"""


class ReasoningEngine:
    def analyze(self, task):
        text = task.lower()

        if any(word in text for word in ["code", "program", "debug", "python"]):
            return {"intent": "coding", "confidence": 0.8}

        if any(word in text for word in ["research", "find", "learn", "explain"]):
            return {"intent": "research", "confidence": 0.8}

        if any(word in text for word in ["schedule", "task", "plan", "remind"]):
            return {"intent": "productivity", "confidence": 0.8}

        if any(word in text for word in ["trade", "market", "forex"]):
            return {"intent": "trading", "confidence": 0.8}

        return {"intent": "general", "confidence": 0.5}
