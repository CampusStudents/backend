from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

EMPTY_TEXT_ERROR = "Value cannot be empty"


class UniversityBaseSchema(BaseModel):
    name: str
    short_name: str
    city_id: UUID

    @field_validator("name", "short_name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(EMPTY_TEXT_ERROR)
        return normalized


class CreateUniversitySchema(UniversityBaseSchema):
    pass


class UpdateUniversitySchema(UniversityBaseSchema):
    pass


class UniversityDTO(UniversityBaseSchema):
    id: UUID
    city_id: UUID | None

    model_config = ConfigDict(from_attributes=True)
