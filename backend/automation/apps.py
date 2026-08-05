"""Application control automation for Offspace."""

import subprocess
import platform


class AppController:
    """Safely launches applications."""

    def open_application(self, command: str):
        system = platform.system()

        if system == "Windows":
            subprocess.Popen(command, shell=True)
        elif system in ("Linux", "Darwin"):
            subprocess.Popen([command])
        else:
            raise RuntimeError("Unsupported operating system")

        return {"status": "opened", "application": command}
