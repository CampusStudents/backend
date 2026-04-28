import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .project_vacancy import ProjectVacancy
    from .user import User

user_skills = Table(
    "user_skills",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="RESTRICT"), primary_key=True),
)

project_vacancy_skills = Table(
    "project_vacancy_skills",
    Base.metadata,
    Column(
        "vacancy_id",
        ForeignKey("project_vacancies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "skill_id",
        ForeignKey("skills.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class City(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "cities"

    name: Mapped[str] = mapped_column(unique=True)


class University(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "universities"

    name: Mapped[str]
    short_name: Mapped[str]
    city_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cities.id", ondelete="RESTRICT")
    )

    city: Mapped[City] = relationship(lazy="joined")


class Skill(UUIDPkMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(100), unique=True)

    users: Mapped[list[User]] = relationship(
        secondary=user_skills,
        back_populates="skills",
    )
    project_vacancies: Mapped[list[ProjectVacancy]] = relationship(
        secondary=project_vacancy_skills,
        back_populates="skills",
    )


class TeamRole(UUIDPkMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
