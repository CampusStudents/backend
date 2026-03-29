from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class UserDTO(BaseModel):
    id: UUID
    email: EmailStr
    roles: list[str] = Field(default_factory=list)
    scopes: set[str] = Field(default_factory=set)
    is_active: bool
    is_verified: bool
    is_profile_completed: bool
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("roles", mode="before")
    @classmethod
    def normalize_roles(cls, value: Any) -> Any:
        if value is None:
            return []
        if isinstance(value, list) and value and hasattr(value[0], "name"):
            return [role.name for role in value]
        return value


class RegisterSchema(BaseModel):
    email: EmailStr
    password: SecretStr

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value: Any) -> Any:
        if not isinstance(value, str):
            raise ValueError("Password must be a string")
        if len(value) < 8:
            raise ValueError("Password must contain at least 8 characters")
        # Длины пароля пока хватит
        # if not re.search(r"[A-Z]", value):
        #     raise ValueError("Password must contain at least one uppercase letter")
        # if not re.search(r"[a-z]", value):
        #     raise ValueError("Password must contain at least one lowercase letter")
        # if not re.search(r"\d", value):
        #     raise ValueError("Password must contain at least one digit")
        # if not re.search(r"[^A-Za-z0-9]", value):
        #     raise ValueError("Password must contain at least one special character")
        return value


class UpdateUserRolesSchema(BaseModel):
    roles: list[str]

    @field_validator("roles")
    @classmethod
    def validate_roles(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Roles list cannot be empty")
        normalized = [role.strip() for role in value if role.strip()]
        if len(normalized) != len(value):
            raise ValueError("Roles must be non-empty strings")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Roles must be unique")
        return normalized
