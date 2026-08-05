class TaskPlanner:
    """Break user goals into manageable tasks."""

    def plan(self, objective):
        return {
            "objective": objective,
            "steps": ["analyze", "execute", "verify"]
        }
