from fastapi import APIRouter
from models.patient import Patient
from models.doctor import Doctor
from models.login import LoginModel

from .v1.auth import(
    signup_doctor_api,
    signup_patient_api,
    login_api    
)


router = APIRouter()


# SIGNUP ROUTE FOR DOCTOR
@router.post("/signup/doctor", summary="Doctor Signup", description="Create a new doctor account")
async def signup_doctor(credentials: Doctor):
    return await signup_doctor_api(credentials)


# SIGNUP ROUTE FOR PATIENT
@router.post("/signup/patient", summary="Patient Signup", description="Create a new patient account")
async def signup_patient(credentials: Patient):
    return await signup_patient_api(credentials)


# LOGIN ROUTE
@router.post("/login", description="Authenticate user with username and password")
async def login(credentials: LoginModel):
    return await login_api(credentials)
