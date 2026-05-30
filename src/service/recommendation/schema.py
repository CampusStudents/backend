from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.db.choices import ProjectFormat, ProjectStatus, ProjectType
from src.service.filters import BaseFilter
from src.service.helpers import EntityDTO, ShortDTO


class VacancyRecommendationFilter(BaseFilter):
    skill_id: UUID | None = None
    team_role_id: UUID | None = None
    event_id: UUID | None = None
    city_id: UUID | None = None
    status: list[ProjectStatus] | None = None
    format: list[ProjectFormat] | None = None
    type: list[ProjectType] | None = None


class RecommendationProjectDTO(BaseModel):
    id: UUID
    title: str
    type: ProjectType
    format: ProjectFormat
    status: ProjectStatus
    owner_id: UUID | None
    city_id: UUID | None
    event_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


class VacancyRecommendationDTO(EntityDTO):
    project_id: UUID
    team_role_id: UUID
    required_count: int
    description: str | None = None
    team_role: ShortDTO
    project: RecommendationProjectDTO
    skills: list[ShortDTO] = Field(default_factory=list)
    matching_skill_count: int
    missing_skill_count: int
    matched_skills: list[ShortDTO] = Field(default_factory=list)
    missing_skills: list[ShortDTO] = Field(default_factory=list)
