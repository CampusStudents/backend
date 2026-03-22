from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import EmailStr, BaseModel, SecretStr, field_validator, ConfigDict

from src.db.models.user import UserRole


class UserDTO(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    is_active: bool
    is_verified: bool
    is_profile_completed: bool
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationRole(str, Enum):
    # copy from src/db/models/user.py
    USER = "user"
    ORGANIZER = "organizer"


class RegisterSchema(BaseModel):
    email: EmailStr
    password: SecretStr
    role: RegistrationRole

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
