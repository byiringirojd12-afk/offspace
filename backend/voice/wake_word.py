class WakeWordDetector:
    """Wake word detection foundation for Offspace."""

    def __init__(self, wake_word="hey offspace"):
        self.wake_word = wake_word.lower()
        self.active = False

    def detect(self, text):
        if not text:
            return False
        return self.wake_word in text.lower()

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
