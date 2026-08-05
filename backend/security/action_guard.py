class ActionGuard:
    """Controls whether an automation action is allowed."""

    def __init__(self):
        self.safe_mode = True

    def authorize(self, action, requires_confirmation=True):
        if self.safe_mode and requires_confirmation:
            return False
        return True

    def enable_safe_mode(self):
        self.safe_mode = True

    def disable_safe_mode(self):
        self.safe_mode = False
