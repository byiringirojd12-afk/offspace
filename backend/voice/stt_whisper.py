"""Whisper speech recognition provider for Offspace."""


class WhisperRecognizer:
    def __init__(self, model_name="base"):
        self.model_name = model_name
        self.model = None

    def load(self):
        try:
            import whisper
            self.model = whisper.load_model(self.model_name)
            return True
        except ImportError:
            return False

    def transcribe(self, audio_file):
        if not self.model:
            raise RuntimeError("Whisper model is not loaded")
        result = self.model.transcribe(audio_file)
        return result.get("text", "")
