from __future__ import annotations
import uuid
from typing import List

from pydantic import BaseModel, Field, field_validator
import core_api.core.constants as constants


class EmployeeBase(BaseModel):
    name: str = Field(
        ...,
        max_length=constants.MAX_EMPLOYEE_NAME_LENGTH,
        description="Employee's name",
    )
    active: bool = Field(
        True, description="If True, the employee will be included on the schedule"
    )

    @field_validator("name")
    @classmethod
    def _strip_and_non_empty(cls, v: str):
        v2 = v.strip()
        if not v2:
            raise ValueError("name cannot be empty or whitespace")
        return v2


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: str | None = Field(None, max_length=constants.MAX_EMPLOYEE_NAME_LENGTH)
    active: bool | None = Field(None)

    @field_validator("name")
    @classmethod
    def _strip_and_non_empty(cls, v: str):
        if v is None:
            return v

        v2 = v.strip()
        if not v2:
            raise ValueError("name cannot be empty or whitespace")
        return v2


class EmployeeOut(EmployeeBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class EmployeeYearReport(BaseModel):
    name: str | None = Field(None, max_length=constants.MAX_EMPLOYEE_NAME_LENGTH)
    months_data: List[EmployeeMonthData]


class EmployeeMonthReport(BaseModel):
    name: str | None = Field(None, max_length=constants.MAX_EMPLOYEE_NAME_LENGTH)
    month_data: EmployeeMonthData


class EmployeeMonthData(BaseModel):
    hours_worked: float
    num_days_off: int
    num_days_worked: int
    num_morning_shifts: int
    num_afternoon_shifts: int
    num_night_shifts: int
