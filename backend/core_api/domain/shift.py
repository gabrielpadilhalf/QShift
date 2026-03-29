from dataclasses import dataclass
from datetime import time
from pydantic import Field
import uuid

@dataclass(frozen=True)
class Shift:
    id: uuid.UUID
    weekday: int = Field(..., ge=0, le=6, description="0 = monday ... 6 = sunday")
    start_time: time = Field(..., description="Local shift start time")
    end_time: time = Field(..., description="Local shift end time")
    min_staff: int = Field(
        1, ge=1, description="Minimum ammount of employees required for the shift"
    )
