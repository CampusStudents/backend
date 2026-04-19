from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class UserProfileBaseSchema(BaseModel):
    first_name: str
    last_name: str
    bio: str | None = None
    city_id: UUID | None = None
    university_id: UUID | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Value cannot be empty")
        return normalized

    @field_validator("bio")
    @classmethod
    def normalize_bio(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CreateUserProfileSchema(UserProfileBaseSchema):
    pass


class UpdateUserProfileSchema(UserProfileBaseSchema):
    pass


class UserProfileDTO(UserProfileBaseSchema):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
