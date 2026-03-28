from __future__ import annotations
import uuid

from datetime import time
from typing import List
from pydantic import BaseModel, Field
import core_api.core.constants as constants
from typing import Optional
from core_api.schemas.shift import PreviewShiftBase
from enum import Enum

class ScheduleOut(BaseModel):
    shifts: List[ScheduleShiftOut]

class ScheduleShiftOutBase(BaseModel):
    weekday: int = Field(..., ge=0, le=6, description="0 = monday ... 6 = sunday")
    start_time: time = Field(..., description="Local shift start time")
    end_time: time = Field(..., description="Local shift end time")
    min_staff: int = Field(
        1, ge=1, description="Minimum amount of employees required for the shift"
    )
    employees: List[ScheduleShiftEmployeeOut]

class ScheduleShiftOut(ScheduleShiftOutBase):
    shift_id: uuid.UUID

    model_config = {"from_attributes": True}

class ScheduleShiftEmployeeOut(BaseModel):
    employee_id: uuid.UUID
    name: str = Field(
        ...,
        max_length=constants.MAX_EMPLOYEE_NAME_LENGTH,
        description="Employee's name",
    )

class ScheduleCreate(BaseModel):
    shifts: List[ScheduleShiftCreate]

class ScheduleShiftCreate(BaseModel):
    shift_id: uuid.UUID
    employee_ids: List[uuid.UUID]

class SchedulePreviewOut(BaseModel):
    possible: bool
    schedule: Optional[PreviewScheduleOut] = None

class PreviewScheduleOut(BaseModel):
    shifts: List[PreviewScheduleShiftOut]

class PreviewScheduleShiftOut(ScheduleShiftOutBase):
    pass

class ShiftVectorIn(BaseModel):
    shift_vector: List[PreviewShiftBase]


class ScheduleGenerationJobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ScheduleGenerationEmployeeOut(BaseModel):
    id: uuid.UUID
    name: str = Field(
        ...,
        max_length=constants.MAX_EMPLOYEE_NAME_LENGTH,
        description="Employee's name",
    )


class ScheduleGenerationAvailabilityOut(BaseModel):
    employee_id: uuid.UUID
    weekday: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time


class ScheduleGenerationDispatchPayload(BaseModel):
    shift_vector: List[PreviewShiftBase]
    employees: List[ScheduleGenerationEmployeeOut]
    availabilities: List[ScheduleGenerationAvailabilityOut]


class ScheduleGenerationDispatchRequest(BaseModel):
    job_id: uuid.UUID
    callback_url: str
    payload: ScheduleGenerationDispatchPayload


class ScheduleGenerationJobAcceptedOut(BaseModel):
    job_id: uuid.UUID
    status: ScheduleGenerationJobStatus


class ScheduleGenerationJobOut(BaseModel):
    job_id: uuid.UUID
    status: ScheduleGenerationJobStatus
    result: Optional[SchedulePreviewOut] = None
    error: Optional[str] = None


class ScheduleGenerationCallbackIn(BaseModel):
    job_id: uuid.UUID
    status: ScheduleGenerationJobStatus
    result: Optional[SchedulePreviewOut] = None
    error: Optional[str] = None
