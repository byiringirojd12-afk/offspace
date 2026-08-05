class VoiceCommandRouter:
    """Routes recognized voice commands to Offspace actions."""

    def __init__(self):
        self.commands = {}

    def register(self, command, handler):
        self.commands[command.lower()] = handler

    def route(self, text):
        if not text:
            return None

        for command, handler in self.commands.items():
            if command in text.lower():
                return handler()

        return None
