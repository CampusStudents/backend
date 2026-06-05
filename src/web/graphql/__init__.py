from strawberry.fastapi import GraphQLRouter

from src.web.graphql.context import get_graphql_context
from src.web.graphql.schema import schema

graphql_router = GraphQLRouter(
    schema,
    context_getter=get_graphql_context,
)
