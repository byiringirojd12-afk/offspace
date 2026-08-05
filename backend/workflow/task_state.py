from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TaskState:
    task_id: str
    goal: str
    status: str = "created"
    steps: list = field(default_factory=list)
    results: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def update_status(self, status):
        self.status = status
