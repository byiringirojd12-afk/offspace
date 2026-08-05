class AutomationRouter:
    """Routes approved commands to automation handlers."""

    def __init__(self):
        self.handlers = {}

    def register(self, name, handler):
        self.handlers[name] = handler

    def execute(self, name, *args, **kwargs):
        if name not in self.handlers:
            raise ValueError(f"Unknown automation action: {name}")
        return self.handlers[name](*args, **kwargs)
