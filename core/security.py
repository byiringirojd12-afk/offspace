from typing import Dict


class PermissionManager:
    def __init__(self):
        self.permissions: Dict[str, bool] = {
            "delete": False,
            "overwrite": False,
            "shutdown": False,
            "format": False,
            "shell": False,
        }

    def has_permission(self, action: str) -> bool:
        return self.permissions.get(action, False)

    def request_permission(self, action: str) -> bool:
        self.permissions[action] = True
        return True

    def revoke_permission(self, action: str) -> None:
        if action in self.permissions:
            self.permissions[action] = False
