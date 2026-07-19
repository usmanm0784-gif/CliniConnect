from fastapi import APIRouter
from models.patient import Patient
from models.doctor import Doctor
from models.login import LoginModel

from .v1.auth import(
    doctor_signup,
    patient_signup,
    login_user    
)


router = APIRouter()

# SIGNUP ROUTE FOR DOCTOR
@router.post("/signup/doctor", summary="Doctor Signup", description="Create a new doctor account")
async def signup(credentials: Doctor):
    return await doctor_signup(credentials)


# SIGNUP ROUTE FOR PATIENT
@router.post("/signup/patient", summary="Patient Signup", description="Create a new patient account")
async def signup_patient(credentials: Patient):
    return await patient_signup(credentials)


# LOGIN ROUTE
@router.post("/login", description="Authenticate user with username and password")
async def login(credentials: LoginModel):
    return await login_user(credentials)
