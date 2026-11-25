import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import pyttsx3
except ImportError:  # pragma: no cover
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover
    sr = None


class VoiceController:
    """Handles wake-word detection, speech recognition, voice activity, and TTS."""

    WAKE_PHRASE = "hey offspace"

    def __init__(self) -> None:
        self.engine = pyttsx3.init() if pyttsx3 is not None else None
        self.recognizer = sr.Recognizer() if sr is not None else None
        self.is_muted = False

    def contains_wake_phrase(self, text: str) -> bool:
        return self.WAKE_PHRASE in text.lower().strip()

    def detect_voice_activity(self, audio_frame: object) -> bool:
        return audio_frame is not None and hasattr(audio_frame, "frame_data")

    def listen_once(self, timeout: float = 5.0, phrase_time_limit: float = 5.0) -> str:
        if self.recognizer is None or sr is None:
            logger.warning("Speech recognition is unavailable in this environment")
            return ""

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand captured speech")
            return ""
        except sr.RequestError as exc:
            logger.warning("Speech recognition service request failed (%s)", type(exc).__name__)
            return ""
        except sr.WaitTimeoutError:
            logger.info("No speech was captured before the microphone timeout")
            return ""
        except OSError as exc:
            logger.warning("Microphone could not be opened (%s)", type(exc).__name__)
            return ""

    def speak(self, text: str) -> str:
        if self.is_muted:
            logger.info("Voice output muted")
            return text

        if self.engine is None:
            logger.info("Text-to-speech is unavailable in this environment")
            return text

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.warning(f"TTS failed: {exc}")
        return text

    def set_microphone_enabled(self, enabled: bool) -> None:
        self.is_muted = not enabled
