from pydantic import BaseModel, field_validator
from datetime import time, date


class AvailabilitySlot(BaseModel):
    date: date
    start_time: time
    end_time: time
    status: str = "available"  

    @field_validator("end_time")
    def validate_time(cls, end_time, info):

        start_time = info.data.get("start_time")

        if start_time and end_time <= start_time:
            raise ValueError(
                "End time must be greater than start time"
            )

        return end_time
    
class DoctorUpdate(BaseModel):
    specialization: str | None = None
    experience: int | None = None
    availability: list[AvailabilitySlot] | None = None
    bio: str | None = None


