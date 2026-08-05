class AudioInput:
    """Microphone input abstraction for Offspace voice system."""

    def __init__(self, device=None):
        self.device = device

    def capture(self):
        """Capture microphone audio.

        Real microphone drivers can be connected here.
        """
        return None

    def list_devices(self):
        return []
