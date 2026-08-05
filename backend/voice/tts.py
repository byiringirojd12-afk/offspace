class SpeechSynthesizer:
    """Text-to-speech interface for Offspace."""

    def __init__(self, engine="piper"):
        self.engine = engine

    def speak(self, text):
        """Generate voice output.

        TTS engine integration will be added here.
        """
        return text
