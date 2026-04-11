import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .project_vacancy import ProjectVacancy
    from .user import User


class Application(UUIDPkMixin, TimestampMixin, Base):
    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("project_vacancies.id", ondelete="CASCADE")
    )
    applicant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    cover_letter: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str]

    decided_at: Mapped[datetime | None]

    vacancy: Mapped["ProjectVacancy"] = relationship(lazy="raise")
    applicant: Mapped["User"] = relationship(lazy="raise")
