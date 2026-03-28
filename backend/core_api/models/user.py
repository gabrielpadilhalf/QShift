from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, DateTime, Index, func, text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "app_user"

    email: Mapped[str] = mapped_column(String(254), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("uq_user_email_ci", text("lower(email)"), unique=True),)

    # relationships
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    weeks: Mapped[list["Week"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    schedule_generation_jobs: Mapped[list["ScheduleGenerationJob"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
