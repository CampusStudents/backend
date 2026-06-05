from strawberry.types import Info

from src.core.exceptions.service.base import ForbiddenError
from src.web.graphql.context import GraphQLContext


def get_context(info: Info) -> GraphQLContext:
    return info.context


def require_scope(info: Info, scope: str) -> None:
    user_scopes = get_context(info).current_user.scopes
    if scope not in user_scopes and "*" not in user_scopes:
        msg = "Insufficient permissions"
        raise ForbiddenError(msg)
