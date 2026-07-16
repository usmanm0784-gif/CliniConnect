from pydantic import BaseModel, field_validator, Field
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
    
class Doctor(BaseModel):
    title: str
    name: str
    phone_number: str
    email: str
    city: str
    password: str = Field(min_length=8)
    specialization: str | None = None
    experience: int | None = None
    bio: str | None = None

class DoctorUpdate(BaseModel):
    title: str | None = None
    name: str | None = None
    phone_number: str | None = None
    city: str | None = None
    specialization: str | None = None
    experience: int | None = None
    bio: str | None = None
