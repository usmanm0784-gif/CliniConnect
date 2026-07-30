from pydantic import BaseModel, field_validator, Field
from datetime import time, date
import re
from .user import UserModel

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
    
class Doctor(UserModel):
    title: str
    name: str
    phone_number: str
    city: str
    specialization: str | None = None
    experience: int | None = None
    bio: str | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        value = re.sub(r"\s+", " ", value)
        value = re.sub(r"[^a-zA-Z\s'-]", "", value)
        if not value:
            raise ValueError("Name cannot be empty")
        return value.title()

    @field_validator("title", "city")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return re.sub(r"\s+", " ", value.strip())

class DoctorUpdate(BaseModel):
    title: str | None = None
    name: str | None = None
    city: str | None = None
    specialization: str | None = None
    experience: int | None = None
    bio: str | None = None
