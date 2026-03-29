from __future__ import annotations
import uuid

from datetime import date, datetime
from typing import List
from sqlalchemy import (
    Date,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
    func,
    text,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY, INTEGER

from .base import Base


class Week(Base):
    __tablename__ = "week"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "start_date"
        ),  # uma semana por segunda-feira por usuário
        UniqueConstraint("user_id", "id"),  # habilita FKs compostas vindas de Shift
        # segunda-feira = 1 no Postgres (0=domingo, 1=segunda, ..., 6=sábado)
        CheckConstraint("EXTRACT(DOW FROM start_date) = 1", name="start_is_monday"),
        CheckConstraint(
            "open_days IS NOT NULL AND cardinality(open_days) >= 1",
            name="open_days_nonempty",
        ),
        CheckConstraint(
            "NOT EXISTS (SELECT 1 FROM unnest(open_days) d WHERE d < 0 OR d > 6)",
            name="open_days_range",
        ),
        Index("ix_week_user_id_approved", "user_id", "approved"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="CASCADE"),
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_days: Mapped[List[int]] = mapped_column(
        ARRAY(INTEGER),
        nullable=False,
        default=[0, 1, 2, 3, 4, 5, 6],
        server_default=text("ARRAY[0,1,2,3,4,5,6]::int[]"),
    )
    approved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="weeks")
    shifts: Mapped[List["Shift"]] = relationship(
        back_populates="week", cascade="all, delete-orphan"
    )
