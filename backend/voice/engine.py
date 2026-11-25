import logging


logger = logging.getLogger(__name__)


class VoiceEngine:
    """Voice pipeline controller for Offspace.

    Uses the existing SpeechRecognition and pyttsx3 dependencies when available.
    """

    def __init__(self, wake_word="hey offspace"):
        self.wake_word = wake_word
        self.active = False

    def listen(self):
        try:
            import speech_recognition as sr
        except ImportError:
            logger.error("Speech recognition dependency is unavailable")
            return None
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                return recognizer.listen(source, timeout=5.0, phrase_time_limit=8.0)
        except sr.WaitTimeoutError:
            logger.info("No speech was captured before the microphone timeout")
            return None
        except OSError as exc:
            logger.warning("Microphone could not be opened (%s)", type(exc).__name__)
            return None

    def recognize(self, audio):
        if audio is None:
            return None
        try:
            import speech_recognition as sr
        except ImportError:
            logger.error("Speech recognition dependency is unavailable")
            return None
        try:
            return sr.Recognizer().recognize_google(audio)
        except sr.UnknownValueError:
            logger.info("Speech recognition could not understand captured speech")
            return None
        except sr.RequestError as exc:
            logger.warning("Speech recognition service request failed (%s)", type(exc).__name__)
            return None

    def speak(self, text):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except ImportError:
            logger.error("Text-to-speech dependency is unavailable")
        except Exception as exc:
            logger.warning("Text-to-speech failed (%s)", type(exc).__name__)
            return text
        return text
