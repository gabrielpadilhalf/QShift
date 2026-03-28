from __future__ import annotations
import uuid

from typing import List
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint, Index, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import core_api.core.constants as constants

from .base import Base


class Employee(Base):
    __tablename__ = "employee"
    __table_args__ = (
        # viabiliza FKs compostas a partir de filhos (user_id, employee_id) -> (user_id, id)
        UniqueConstraint("user_id", "id"),
        Index("ix_employee_user_id_active", "user_id", "active"),
        Index("ix_employee_user_id_name", "user_id", "name"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "app_user.id", ondelete="CASCADE"
        ),  # referencia User(id), escopo completo via UNIQUE(user_id,id)
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(constants.MAX_EMPLOYEE_NAME_LENGTH), nullable=False
    )
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="employees")
    availabilities: Mapped[List["Availability"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["ShiftAssignment"]] = relationship(
        "ShiftAssignment",
        back_populates="employee",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(ShiftAssignment.user_id==Employee.user_id, "
            "ShiftAssignment.employee_id==Employee.id)"
        ),
        foreign_keys="[ShiftAssignment.user_id, ShiftAssignment.employee_id]",
        overlaps="shift,assignments",
    )
