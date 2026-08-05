class VoiceEngine:
    """Voice pipeline controller for Offspace.

    Phase 3 foundation. Speech recognition and synthesis providers
    will plug into this interface.
    """

    def __init__(self, wake_word="hey offspace"):
        self.wake_word = wake_word
        self.active = False

    def listen(self):
        """Capture audio input placeholder."""
        return None

    def recognize(self, audio):
        """Convert audio to text using future STT provider."""
        return None

    def speak(self, text):
        """Send text to future TTS provider."""
        return text
