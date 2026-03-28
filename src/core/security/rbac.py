from collections.abc import Iterable

from src.db.models import User


def build_scope(subject: str, action: str) -> str:
    if subject == "*" and action == "*":
        return "*"
    if action == "*":
        return f"{subject}:*"
    return f"{subject}:{action}"


def get_user_scopes(user: User) -> set[str]:
    scopes: set[str] = set()
    for role in user.roles:
        for permission in role.permissions:
            scopes.add(build_scope(permission.subject, permission.action))
    return scopes


def normalize_scopes(scopes: Iterable[str]) -> list[str]:
    return [scope.strip() for scope in scopes if scope.strip()]
