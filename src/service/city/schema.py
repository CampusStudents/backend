from pydantic import BaseModel

from src.service.filters import BaseFilter
from src.service.helpers import EntityDTO, NonEmptyStr


class CityBaseSchema(BaseModel):
    name: NonEmptyStr


class CreateCitySchema(CityBaseSchema):
    pass


class UpdateCitySchema(BaseModel):
    name: NonEmptyStr | None = None


class CityFilter(BaseFilter):
    name__like: str | None = None


class CityDTO(CityBaseSchema, EntityDTO):
    pass
