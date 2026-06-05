from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from src.service.helpers import EntityDTO, NonEmptyStr, ShortDTO

SKILL_IDS_UNIQUE_ERROR = "Skill ids must be unique"
PROJECT_LINK_URL_ERROR = "Project link must be a valid URL"
WORK_PERIOD_ORDER_ERROR = "Work ended date must not be before work started date"


class PortfolioItemBaseSchema(BaseModel):
    title: NonEmptyStr
    description: NonEmptyStr | None = None
    work_started_at: date | None = None
    work_ended_at: date | None = None
    team_role_id: UUID
    project_link: HttpUrl | None = None

    @model_validator(mode="after")
    def validate_work_period(self):
        if (
            self.work_started_at is not None
            and self.work_ended_at is not None
            and self.work_ended_at < self.work_started_at
        ):
            raise ValueError(WORK_PERIOD_ORDER_ERROR)
        return self


class CreatePortfolioItemSchema(PortfolioItemBaseSchema):
    pass


class UpdatePortfolioItemSchema(BaseModel):
    title: NonEmptyStr | None = None
    description: NonEmptyStr | None = None
    work_started_at: date | None = None
    work_ended_at: date | None = None
    team_role_id: UUID | None = None
    project_link: HttpUrl | None = None

    @model_validator(mode="after")
    def validate_work_period(self):
        if (
            self.work_started_at is not None
            and self.work_ended_at is not None
            and self.work_ended_at < self.work_started_at
        ):
            raise ValueError(WORK_PERIOD_ORDER_ERROR)
        return self


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
