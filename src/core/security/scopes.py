def scope(subject: str, action: str) -> str:
    return f"{subject}:{action}"


class Scope:
    AUTH_ME = scope("auth", "me")
    AUTH_LOGOUT = scope("auth", "logout")
    AUTH_CHANGE_PASSWORD = scope("auth", "change_password")
    AUTH_QUIT_ALL = scope("auth", "quit_all")
    AUTH_RESEND_VERIFICATION = scope("auth", "resend_verification")
    USERS_UPDATE_ROLES = scope("users", "update_roles")
    MONITORING_HEALTH = scope("monitoring", "health")
