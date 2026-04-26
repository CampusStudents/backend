from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.service.helpers import NonEmptyStr


class UserProfileBaseSchema(BaseModel):
    first_name: NonEmptyStr
    last_name: NonEmptyStr
    bio: NonEmptyStr | None = None
    city_id: UUID
    university_id: UUID


class CreateUserProfileSchema(UserProfileBaseSchema):
    pass


class UpdateUserProfileSchema(BaseModel):
    first_name: NonEmptyStr | None = None
    last_name: NonEmptyStr | None = None
    bio: NonEmptyStr | None = None
    city_id: UUID | None = None
    university_id: UUID | None = None


class UserProfileDTO(UserProfileBaseSchema):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
