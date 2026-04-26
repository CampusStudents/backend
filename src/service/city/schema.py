from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.service.helpers import NonEmptyStr


class CityBaseSchema(BaseModel):
    name: NonEmptyStr


class CreateCitySchema(CityBaseSchema):
    pass


class UpdateCitySchema(BaseModel):
    name: NonEmptyStr | None = None


class CityDTO(CityBaseSchema):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
