from __future__ import annotations
import uuid

from datetime import date, datetime
from typing import List
from pydantic import BaseModel, Field, model_validator


class WeekBase(BaseModel):
    start_date: date = Field(..., description="Week start date (must be a monday)")
    open_days: List[int] = Field(
        default_factory=lambda: [0, 1, 2, 3, 4, 5, 6],
        description="Weekdays open: 0=Mon ... 6=Sun",
    )

    @model_validator(mode="after")
    def _validate_week(self):
        if self.start_date.weekday() != 0:
            raise ValueError("start_date must be a Monday")

        if not self.open_days:
            raise ValueError("open_days must not be empty")

        if any(d < 0 or d > 6 for d in self.open_days):
            raise ValueError("open_days must contain integers in [0,6]")

        self.open_days = sorted(set(self.open_days))
        return self


class WeekCreate(WeekBase):
    pass


class WeekUpdate(BaseModel):
    open_days: List[int] | None = None

    @model_validator(mode="after")
    def _validate_open_days(self):
        if self.open_days is not None:
            if not self.open_days:
                raise ValueError("open_days must not be empty")

            if any(d < 0 or d > 6 for d in self.open_days):
                raise ValueError("open_days must contain integers in [0,6]")

            self.open_days = sorted(set(self.open_days))
        return self


class WeekOut(WeekBase):
    id: uuid.UUID
    user_id: uuid.UUID
    approved: bool
    approved_at: datetime | None = None

    model_config = {"from_attributes": True}
