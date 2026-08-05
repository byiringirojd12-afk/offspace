from enum import Enum


class PermissionLevel(Enum):
    USER = "user"
    TRUSTED = "trusted"
    ADMIN = "admin"


class PermissionManager:
    def __init__(self, level=PermissionLevel.USER):
        self.level = level

    def can_execute(self, action):
        dangerous = {"delete_file", "system_change", "network_change"}
        if action in dangerous:
            return self.level == PermissionLevel.ADMIN
        return True
