from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

from src.service.helpers import EntityDTO, NonEmptyStr, ShortDTO

SKILL_IDS_UNIQUE_ERROR = "Skill ids must be unique"
PROJECT_LINK_URL_ERROR = "Project link must be a valid URL"


class PortfolioItemBaseSchema(BaseModel):
    title: NonEmptyStr
    description: NonEmptyStr | None = None
    team_role_id: UUID
    project_link: HttpUrl | None = None

class CreatePortfolioItemSchema(PortfolioItemBaseSchema):
    pass


class UpdatePortfolioItemSchema(BaseModel):
    title: NonEmptyStr | None = None
    description: NonEmptyStr | None = None
    team_role_id: UUID | None = None
    project_link: HttpUrl | None = None


class PortfolioItemDTO(PortfolioItemBaseSchema, EntityDTO):
    user_id: UUID
    team_role: ShortDTO


class ReplaceUserSkillsSchema(BaseModel):
    skill_ids: list[UUID] = Field(default_factory=list)

    @field_validator("skill_ids")
    @classmethod
    def validate_unique_skill_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) != len(value):
            raise ValueError(SKILL_IDS_UNIQUE_ERROR)
        return value
