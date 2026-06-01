from sqlalchemy import Select
from sqlalchemy.orm import selectinload

from src.db.models import TeamMember, User
from src.db.repository.base import SQLAlchemyRepository


class TeamMemberRepository(SQLAlchemyRepository):
    model = TeamMember

    def apply_related_load(
        self,
        query: Select[tuple[TeamMember]],
    ) -> Select[tuple[TeamMember]]:
        return query.options(
            selectinload(TeamMember.user).selectinload(User.profile),
            selectinload(TeamMember.team_role),
        )
