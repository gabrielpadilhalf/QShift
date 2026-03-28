from __future__ import annotations
import uuid

from pydantic import BaseModel, Field, model_validator
from datetime import date, time


class ShiftBase(BaseModel):
    weekday: int = Field(..., ge=0, le=6, description="0 = monday ... 6 = sunday")
    start_time: time = Field(..., description="Local shift start time")
    end_time: time = Field(..., description="Local shift end time")
    min_staff: int = Field(
        1, ge=1, description="Minimum ammount of employees required for the shift"
    )

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be greater than start_time")
        return self


class ShiftCreate(ShiftBase):
    pass

class PreviewShiftBase(ShiftBase):
    id: uuid.UUID

class ShiftUpdate(BaseModel):
    weekday: int | None = Field(None, ge=0, le=6)
    start_time: time | None = Field(None)
    end_time: time | None = Field(None)
    min_staff: int | None = Field(None, ge=1)

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be greater than start_time")
        return self


class ShiftOut(ShiftBase):
    id: uuid.UUID
    user_id: uuid.UUID
    week_id: uuid.UUID
    local_date: date

    model_config = {"from_attributes": True}
