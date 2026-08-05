"""System automation utilities."""

import platform


class SystemController:
    def get_system_info(self):
        return {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        }
