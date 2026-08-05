class SpeechRecognizer:
    """Speech-to-text interface for Offspace voice pipeline."""

    def __init__(self, engine="local"):
        self.engine = engine

    def transcribe(self, audio):
        """Convert audio input into text.

        Engine integration will be added with Whisper/Vosk.
        """
        return ""
