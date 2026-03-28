from __future__ import annotations
import uuid

from sqlalchemy import (
    ForeignKeyConstraint,
    UniqueConstraint,
    func,
    Index,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class ShiftAssignment(Base):
    __tablename__ = "shift_assignment"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "shift_id", "employee_id", name="uq_assignment_unique"
        ),
        ForeignKeyConstraint(
            ["user_id", "shift_id"],
            ["shift.user_id", "shift.id"],
            ondelete="CASCADE",
            name="fk_assignment_shift_user_scoped",
        ),
        ForeignKeyConstraint(
            ["user_id", "employee_id"],
            ["employee.user_id", "employee.id"],
            ondelete="CASCADE",
            name="fk_assignment_employee_user_scoped",
        ),
        Index("ix_assignment_user_shift", "user_id", "shift_id"),
        Index("ix_assignment_user_employee", "user_id", "employee_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    shift_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    shift: Mapped["Shift"] = relationship(
        "Shift",
        back_populates="assignments",
        primaryjoin=(
            "and_(ShiftAssignment.user_id==Shift.user_id, "
            "ShiftAssignment.shift_id==Shift.id)"
        ),
        foreign_keys="[ShiftAssignment.user_id, ShiftAssignment.shift_id]",
        overlaps="employee,assignments",
    )

    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="assignments",
        primaryjoin=(
            "and_(ShiftAssignment.user_id==Employee.user_id, "
            "ShiftAssignment.employee_id==Employee.id)"
        ),
        foreign_keys="[ShiftAssignment.user_id, ShiftAssignment.employee_id]",
        overlaps="shift,assignments",
    )
