class VoiceLoop:
    """Main voice interaction loop for Offspace."""

    def __init__(self, engine):
        self.engine = engine
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def process(self):
        if not self.running:
            return None

        audio = self.engine.listen()
        text = self.engine.recognize(audio)
        return text
