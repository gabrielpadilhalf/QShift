from __future__ import annotations
import uuid

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Text, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class ScheduleGenerationJob(Base):
    __tablename__ = "schedule_generation_job"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'done', 'failed')",
            name="schedule_generation_job_status_valid",
        ),
        Index("ix_schedule_generation_job_user_status", "user_id", "status"),
        Index("ix_schedule_generation_job_user_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    request_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    result_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="schedule_generation_jobs")
