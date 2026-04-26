import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .application import Application
    from .library import Skill, TeamRole
    from .project import Project

from .library import project_vacancy_skills


class ProjectVacancy(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "project_vacancies"
    __table_args__ = (
        CheckConstraint(
            "required_count > 0",
            name="ck_project_vacancies_required_count_positive",
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    team_role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("team_roles.id", ondelete="RESTRICT")
    )

    required_count: Mapped[int]
    description: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="vacancies")
    team_role: Mapped[TeamRole] = relationship(lazy="joined")
    skills: Mapped[list[Skill]] = relationship(
        secondary=project_vacancy_skills,
        back_populates="project_vacancies",
    )
    applications: Mapped[list[Application]] = relationship(
        back_populates="vacancy",
    )
