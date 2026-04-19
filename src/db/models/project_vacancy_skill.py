from sqlalchemy import Column, ForeignKey, Table

from .base import Base

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
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
