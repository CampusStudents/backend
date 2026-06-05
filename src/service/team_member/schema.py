from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from src.service.helpers import EntityDTO


class TeamMemberUserProfileDTO(BaseModel):
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class TeamMemberUserDTO(BaseModel):
    id: UUID
    email: EmailStr
    profile: TeamMemberUserProfileDTO | None = None

    model_config = ConfigDict(from_attributes=True)


class TeamMemberTeamRoleDTO(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class TeamMemberDTO(EntityDTO):
    project_id: UUID
    user_id: UUID
    team_role_id: UUID | None
    joined_at: datetime
    user: TeamMemberUserDTO
    team_role: TeamMemberTeamRoleDTO | None = None
