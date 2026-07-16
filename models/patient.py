from pydantic import BaseModel, Field

class Patient(BaseModel):
    name: str
    phone_number: str
    email: str
    password: str = Field(min_length=8)
    doctor_notes: str = None