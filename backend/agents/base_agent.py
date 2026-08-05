class BaseAgent:
    """Base interface for Offspace specialized agents."""

    name = "base"

    def run(self, task):
        raise NotImplementedError("Agent must implement run()")
