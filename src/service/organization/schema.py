from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from src.service.filters import BaseFilter
from src.service.helpers import EntityDTO, NonEmptyStr


class OrganizationBaseSchema(BaseModel):
    owner_user_id: UUID | None = None
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    ]
    description: NonEmptyStr | None = None
    contact_email: EmailStr


class CreateOrganizationSchema(OrganizationBaseSchema):
    pass


class UpdateOrganizationSchema(BaseModel):
    owner_user_id: UUID | None = None
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    ] | None = None
    description: str | None = None
    contact_email: EmailStr | None = None


class OrganizationFilter(BaseFilter):
    name__like: str | None = None
    owner_user_id__in: list[UUID] | None = Field(default=None, alias="owner_user_id")


class OrganizationOwnerDTO(BaseModel):
    id: UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class OrganizationDTO(OrganizationBaseSchema, EntityDTO):
    owner: OrganizationOwnerDTO | None = None
