from datetime import datetime
from typing import TYPE_CHECKING
from app.core.db_async import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime


if TYPE_CHECKING:
    from app.models.enrollments import Enrollment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(10), default="student")
    is_active: Mapped[bool] = mapped_column(default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None)

    # relationship
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="user",  lazy="selectin"
    )
