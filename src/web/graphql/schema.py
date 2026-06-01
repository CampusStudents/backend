import strawberry

from src.web.graphql import skills as skill_graphql


@strawberry.type
class Query:
    skills: list[skill_graphql.SkillType] = strawberry.field(
        resolver=skill_graphql.get_skills,
    )
    skill: skill_graphql.SkillType = strawberry.field(
        resolver=skill_graphql.get_skill,
    )


@strawberry.type
class Mutation:
    create_skill: skill_graphql.SkillType = strawberry.field(
        resolver=skill_graphql.create_skill,
    )
    update_skill: skill_graphql.SkillType = strawberry.field(
        resolver=skill_graphql.update_skill,
    )
    delete_skill: bool = strawberry.field(resolver=skill_graphql.delete_skill)


schema = strawberry.Schema(query=Query, mutation=Mutation)
