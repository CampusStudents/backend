from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from src.db.choices import OrganizationRequestStatus
from src.service.filters import BaseFilter
from src.service.helpers import EntityDTO, NonEmptyStr


class CreateOrganizationRequestSchema(BaseModel):
    organization_name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    ]
    description: NonEmptyStr | None = None
    contact_email: EmailStr


class RejectOrganizationRequestSchema(BaseModel):
    reject_reason: NonEmptyStr


class OrganizationRequestFilter(BaseFilter):
    status__in: list[OrganizationRequestStatus] | None = Field(
        default=None,
        alias="status",
    )
    user_id__in: list[UUID] | None = Field(default=None, alias="user_id")


class OrganizationRequestUserDTO(BaseModel):
    id: UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class OrganizationRequestDTO(EntityDTO):
    user_id: UUID
    organization_name: str
    description: str | None = None
    contact_email: EmailStr
    status: OrganizationRequestStatus
    reviewed_by_id: UUID | None = None
    reviewed_at: datetime | None = None
    reject_reason: str | None = None
    user: OrganizationRequestUserDTO
    reviewed_by: OrganizationRequestUserDTO | None = None
