import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def configure_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
) -> None:
    """Configure base logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format=LOG_DEFAULT_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class RunConfig(BaseModel):
    host: str = "localhost"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    users: str = "/users"
    auth: str = "/auth"
    cities: str = "/cities"
    universities: str = "/universities"
    projects: str = "/projects"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class AuthConfig(BaseModel):
    private_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    refresh_token_expire_days: int = 30
    access_token_expire_minutes: int = 15
    access_token_type: str = "access"
    refresh_token_type: str = "refresh"
    token_version_field: str = "token_version"


class RBACConfig(BaseModel):
    initial_subjects: list[str] = [
        "users",
        "cities",
        "universities",
        "user_profiles",
        "projects",
        "project_vacancies",
    ]
    initial_actions: list[str] = [
        "detail",
        "list",
        "create",
        "update",
        "delete",
    ]
    initial_permission_schema: dict[str, list[str]] = {
        "admin": ["*"],
        "public": [
            "auth:login",
            "auth:register",
            "auth:refresh",
            "auth:verify",
            "auth:forgot_password",
            "auth:reset_password",
        ],
        "user": [
            "auth:me",
            "auth:logout",
            "auth:change_password",
            "auth:quit_all",
            "auth:resend_verification",
            "cities:list",
            "cities:detail",
            "universities:list",
            "universities:detail",
            "user_profiles:detail",
            "user_profiles:create",
            "user_profiles:update",
            "projects:list",
            "projects:detail",
            "projects:create",
            "projects:update",
            "projects:delete",
            "project_vacancies:list",
            "project_vacancies:detail",
            "project_vacancies:create",
            "project_vacancies:update",
            "project_vacancies:delete",
        ],
    }
    admin_email: str = "admin@example.com"
    admin_password: str = "admin"
    public_role_name: str = "public"
    admin_role_name: str = "admin"


class EmailConfig(BaseModel):
    smtp_host: str = "maildev"
    smtp_port: int = 1025
    from_email: str = "campus@mail.ru"


class DatabaseConfig(BaseModel):
    drivername: str = "postgresql+asyncpg"
    user: str
    password: str
    name: str
    host: str
    port: int
    echo: bool = False
    pool_size: int = 50
    echo_pool: bool = False
    max_overflow: int = 10
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> URL:
        return URL.create(
            drivername=self.drivername,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    auth: AuthConfig = AuthConfig()
    rbac: RBACConfig
    email: EmailConfig = EmailConfig()
    db: DatabaseConfig
    app_url: str = "127.0.0.1:8000"


settings = Settings()
