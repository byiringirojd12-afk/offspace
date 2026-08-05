from datetime import datetime


class AuditLog:
    """Tracks automation decisions and actions."""

    def __init__(self):
        self.events = []

    def record(self, action, status):
        self.events.append({
            "action": action,
            "status": status,
            "time": datetime.utcnow().isoformat()
        })

    def all_events(self):
        return self.events
