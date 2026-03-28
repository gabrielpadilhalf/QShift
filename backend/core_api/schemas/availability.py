from __future__ import annotations
import uuid

from pydantic import BaseModel, Field, model_validator
from datetime import time


class AvailabilityBase(BaseModel):
    weekday: int = Field(..., ge=0, le=6, description="0 = monday ... 6 = sunday")
    start_time: time = Field(..., description="Local start time")
    end_time: time = Field(..., description="Local end time")

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be greater than start_time")
        return self


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    weekday: int | None = Field(None, ge=0, le=6)
    start_time: time | None = Field(None)
    end_time: time | None = Field(None)

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be greater than start_time")
        return self


class AvailabilityOut(AvailabilityBase):
    id: uuid.UUID
    user_id: uuid.UUID
    employee_id: uuid.UUID

    model_config = {"from_attributes": True}
