"""Piper text-to-speech provider for Offspace."""

import subprocess


class PiperSynthesizer:
    def __init__(self, voice_model=None):
        self.voice_model = voice_model

    def speak(self, text, output_file="response.wav"):
        command = ["piper", "--output_file", output_file]
        if self.voice_model:
            command.extend(["--model", self.voice_model])
        process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
        process.communicate(text)
        return output_file
