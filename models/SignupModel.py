from pydantic import BaseModel, Field

class SignupModelDoctor(BaseModel):
    title: str
    name: str
    phone_number: str
    email: str
    city: str
    specialization: str
    password: str = Field(min_length=8)

class SignupModelPatient(BaseModel):
    name: str
    phone_number: str
    email: str
    password: str = Field(min_length=8)
    doctor_notes: str = None