from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from src.db.choices import ProjectFormat, ProjectStatus, ProjectType
from src.service.helpers import NonEmptyStr

INVALID_INITIAL_STATUS_ERROR = "Project cannot be created as ended or canceled"


class ProjectBaseSchema(BaseModel):
    title: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    ]
    description: str | None = None
    type: ProjectType
    format: ProjectFormat
    deadline: datetime | None = None
    status: ProjectStatus = ProjectStatus.NEW
    city_id: UUID | None = None
    event_id: UUID | None = None

    @field_validator("description", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CreateProjectSchema(ProjectBaseSchema):
    @field_validator("status")
    @classmethod
    def validate_initial_status(cls, value: ProjectStatus) -> ProjectStatus:
        if value in {ProjectStatus.ENDED, ProjectStatus.CANCELED}:
            raise ValueError(INVALID_INITIAL_STATUS_ERROR)
        return value


class UpdateProjectSchema(BaseModel):
    title: NonEmptyStr | None = None
    description: str | None = None
    type: ProjectType | None = None
    format: ProjectFormat | None = None
    deadline: datetime | None = None
    status: ProjectStatus | None = None
    city_id: UUID | None = None
    event_id: UUID | None = None

    @field_validator("description", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class ProjectDTO(ProjectBaseSchema):
    id: UUID
    owner_id: UUID | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
