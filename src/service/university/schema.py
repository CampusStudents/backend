from uuid import UUID

from pydantic import BaseModel, Field

from src.service.filters import BaseFilter
from src.service.helpers import EntityDTO, NonEmptyStr


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


class UniversityFilter(BaseFilter):
    name__like: str | None = None
    city_id__in: list[UUID] | None = Field(default=None, alias="city_id")


class UniversityDTO(UniversityBaseSchema, EntityDTO):
    pass
