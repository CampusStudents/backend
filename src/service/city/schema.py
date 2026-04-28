from pydantic import BaseModel

from src.service.helpers import EntityDTO, NonEmptyStr


class CityBaseSchema(BaseModel):
    name: NonEmptyStr


class CreateCitySchema(CityBaseSchema):
    pass


class UpdateCitySchema(BaseModel):
    name: NonEmptyStr | None = None


class CityDTO(CityBaseSchema, EntityDTO):
    pass
