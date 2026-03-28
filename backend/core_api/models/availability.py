from __future__ import annotations
import uuid

from datetime import time
from sqlalchemy import (
    Time,
    Integer,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class Availability(Base):
    __tablename__ = "availability"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "employee_id",
            "weekday",
            "start_time",
            "end_time",
            name="uq_availability_slot",
        ),
        CheckConstraint("weekday BETWEEN 0 AND 6", name="weekday_range"),
        CheckConstraint("end_time > start_time", name="availability_time_ok"),
        ForeignKeyConstraint(
            ["user_id", "employee_id"],
            ["employee.user_id", "employee.id"],
            ondelete="CASCADE",
            name="fk_availability_employee_user_scoped",
        ),
        Index(
            "ix_availability_user_employee_weekday", "user_id", "employee_id", "weekday"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    # relationships
    employee: Mapped["Employee"] = relationship(back_populates="availabilities")
