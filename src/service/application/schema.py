from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from src.db.choices import ApplicationStatus, ProjectStatus
from src.service.helpers import EntityDTO, NonEmptyStr


class CreateApplicationSchema(BaseModel):
    cover_letter: NonEmptyStr | None = None


class ApplicationDecisionSchema(BaseModel):
    status: Literal[ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED]


class ApplicationApplicantProfileDTO(BaseModel):
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationApplicantDTO(BaseModel):
    id: UUID
    email: EmailStr
    profile: ApplicationApplicantProfileDTO | None = None

    model_config = ConfigDict(from_attributes=True)


class ApplicationTeamRoleDTO(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationProjectDTO(BaseModel):
    id: UUID
    title: str
    status: ProjectStatus
    owner_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


class ApplicationVacancyDTO(BaseModel):
    id: UUID
    project_id: UUID
    team_role_id: UUID
    required_count: int
    description: str | None = None
    team_role: ApplicationTeamRoleDTO
    project: ApplicationProjectDTO

    model_config = ConfigDict(from_attributes=True)


class ApplicationDTO(EntityDTO):
    vacancy_id: UUID
    applicant_id: UUID
    cover_letter: NonEmptyStr | None = None
    status: ApplicationStatus
    decided_at: datetime | None = None
    applicant: ApplicationApplicantDTO
    vacancy: ApplicationVacancyDTO
