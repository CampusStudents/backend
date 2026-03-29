from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import UUIDPkMixin, TimestampMixin


class City(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "cities"
    name: Mapped[str] = mapped_column(unique=True)
