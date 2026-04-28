from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.service.helpers import EntityDTO, ShortDTO

SKILL_IDS_UNIQUE_ERROR = "Skill ids must be unique"


class ProjectVacancyBaseSchema(BaseModel):
    team_role_id: UUID
    required_count: int = Field(gt=0)
    description: str | None = None
    skill_ids: list[UUID] = Field(default_factory=list)

    @field_validator("description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("skill_ids")
    @classmethod
    def validate_unique_skill_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) != len(value):
            raise ValueError(SKILL_IDS_UNIQUE_ERROR)
        return value


class CreateProjectVacancySchema(ProjectVacancyBaseSchema):
    pass


class UpdateProjectVacancySchema(BaseModel):
    team_role_id: UUID | None = None
    required_count: int | None = Field(default=None, gt=0)
    description: str | None = None
    skill_ids: list[UUID] | None = None

    @field_validator("description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("skill_ids")
    @classmethod
    def validate_unique_skill_ids(cls, value: list[UUID] | None) -> list[UUID] | None:
        if value is not None and len(set(value)) != len(value):
            raise ValueError(SKILL_IDS_UNIQUE_ERROR)
        return value


class ProjectVacancyDTO(ProjectVacancyBaseSchema, EntityDTO):
    project_id: UUID
    skills: list[ShortDTO]
