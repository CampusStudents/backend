import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.choices import ApplicationStatus, enum_values

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .project_vacancy import ProjectVacancy
    from .user import User


class Application(UUIDPkMixin, TimestampMixin, Base):
    __table_args__ = (
        UniqueConstraint(
            "vacancy_id",
            "applicant_id",
            name="uq_applications_vacancy_id_applicant_id",
        ),
    )

    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("project_vacancies.id", ondelete="CASCADE")
    )
    applicant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    cover_letter: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ApplicationStatus] = mapped_column(
        SQLAlchemyEnum(
            ApplicationStatus,
            name="application_status",
            values_callable=enum_values,
        ),
        default=ApplicationStatus.PENDING,
    )

    decided_at: Mapped[datetime | None]

    vacancy: Mapped[ProjectVacancy] = relationship(back_populates="applications")
    applicant: Mapped[User] = relationship(back_populates="applications")
