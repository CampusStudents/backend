from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.service.helpers import NonEmptyStr


class UniversityBaseSchema(BaseModel):
    name: NonEmptyStr
    short_name: NonEmptyStr
    city_id: UUID


class CreateUniversitySchema(UniversityBaseSchema):
    pass


class UpdateUniversitySchema(BaseModel):
    name: NonEmptyStr | None = None
    short_name: NonEmptyStr | None = None
    city_id: UUID | None = None


class UniversityDTO(UniversityBaseSchema):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
