def scope(subject: str, action: str) -> str:
    return f"{subject}:{action}"


class Scope:
    AUTH_ME = scope("auth", "me")
    AUTH_LOGOUT = scope("auth", "logout")
    AUTH_CHANGE_PASSWORD = scope("auth", "change_password")
    AUTH_QUIT_ALL = scope("auth", "quit_all")
    AUTH_RESEND_VERIFICATION = scope("auth", "resend_verification")
    CITIES_LIST = scope("cities", "list")
    CITIES_DETAIL = scope("cities", "detail")
    CITIES_CREATE = scope("cities", "create")
    CITIES_UPDATE = scope("cities", "update")
    CITIES_DELETE = scope("cities", "delete")
    UNIVERSITIES_LIST = scope("universities", "list")
    UNIVERSITIES_DETAIL = scope("universities", "detail")
    UNIVERSITIES_CREATE = scope("universities", "create")
    UNIVERSITIES_UPDATE = scope("universities", "update")
    UNIVERSITIES_DELETE = scope("universities", "delete")
    USER_PROFILES_DETAIL = scope("user_profiles", "detail")
    USER_PROFILES_DETAIL_ANY = scope("user_profiles", "detail_any")
    USER_PROFILES_CREATE = scope("user_profiles", "create")
    USER_PROFILES_UPDATE = scope("user_profiles", "update")
    USERS_UPDATE_ROLES = scope("users", "update_roles")
    MONITORING_HEALTH = scope("monitoring", "health")
