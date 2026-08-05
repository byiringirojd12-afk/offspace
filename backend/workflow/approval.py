class ApprovalCheckpoint:
    """Human approval checkpoint for sensitive workflow steps."""

    def __init__(self):
        self.pending = []

    def request(self, action):
        self.pending.append(action)
        return {
            "requires_approval": True,
            "action": action
        }

    def approve(self, action):
        if action in self.pending:
            self.pending.remove(action)
            return True
        return False
