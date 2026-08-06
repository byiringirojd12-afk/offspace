from enum import Enum


class Permission(str, Enum):
    USER = "user"
    ADMIN = "admin"


def require_permission(required_permission: Permission, current_permission: Permission) -> bool:
    return current_permission == required_permission or current_permission == Permission.ADMIN
