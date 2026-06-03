from typing import TYPE_CHECKING
from app.core.db_async import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime
from datetime import datetime


if TYPE_CHECKING:
    from app.models.enrollments import Enrollment


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None)

    # relationship
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="course", lazy="selectin"
    )
