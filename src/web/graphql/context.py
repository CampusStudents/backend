from dataclasses import dataclass
from typing import Annotated

from fastapi import Security

from src.service.skill.service import SkillService
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    SkillServiceDep,
    get_current_active_user,
)


@dataclass(frozen=True, slots=True)
class GraphQLContext:
    current_user: UserDTO
    skill_service: SkillService


async def get_graphql_context(
    current_user: Annotated[
        UserDTO,
        Security(get_current_active_user, scopes=[]),
    ],
    skill_service: SkillServiceDep,
) -> GraphQLContext:
    return GraphQLContext(
        current_user=current_user,
        skill_service=skill_service,
    )
