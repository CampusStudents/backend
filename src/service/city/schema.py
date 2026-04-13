from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

class CityBaseSchema(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("City name cannot be empty")
        return normalized


class CreateCitySchema(CityBaseSchema):
    pass

class UpdateCitySchema(BaseModel):
    pass


class CityDTO(CityBaseSchema):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
