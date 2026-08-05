from datetime import datetime


class WorkflowProgress:
    """Tracks workflow execution progress."""

    def __init__(self):
        self.events = []

    def update(self, task_id, step, status):
        self.events.append({
            "task_id": task_id,
            "step": step,
            "status": status,
            "time": datetime.utcnow().isoformat()
        })

    def history(self):
        return self.events
