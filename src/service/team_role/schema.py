from pydantic import BaseModel

from src.service.filters import BaseFilter
from src.service.helpers import EntityDTO, NonEmptyStr


class TeamRoleBaseSchema(BaseModel):
    name: NonEmptyStr
    description: NonEmptyStr | None = None


class CreateTeamRoleSchema(TeamRoleBaseSchema):
    pass


class UpdateTeamRoleSchema(BaseModel):
    name: NonEmptyStr | None = None
    description: NonEmptyStr | None = None


class TeamRoleFilter(BaseFilter):
    name: NonEmptyStr | None = None
    name__like: str | None = None


class TeamRoleDTO(TeamRoleBaseSchema, EntityDTO):
    pass
