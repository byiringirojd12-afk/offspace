"""Context management foundation for Offspace reasoning."""


class ContextManager:
    def __init__(self):
        self.context = []

    def add(self, item):
        self.context.append(item)

    def get(self):
        return list(self.context)
