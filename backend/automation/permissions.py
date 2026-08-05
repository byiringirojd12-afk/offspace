class PermissionManager:
    """Controls approval before sensitive computer actions."""

    def __init__(self):
        self.allowed_actions = set()

    def allow(self, action):
        self.allowed_actions.add(action)

    def can_execute(self, action):
        return action in self.allowed_actions
