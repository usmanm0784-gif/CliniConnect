from pydantic import field_validator
import re
from .user import UserModel

class Patient(UserModel):
    name: str
    phone_number: str
    doctor_notes: str = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        value = re.sub(r"\s+", " ", value)
        value = re.sub(r"[^a-zA-Z\s'-]", "", value)
        if not value:
            raise ValueError("Name cannot be empty")
        return value.title()