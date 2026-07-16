from fastapi import APIRouter
from models.patient import Patient
from models.doctor import Doctor
from models.login import LoginModel

from services.auth_service import (
    doctor_signup,
    patient_signup,
    login_user
)

router = APIRouter()

# SIGNUP ROUTE FOR DOCTOR
@router.post("/signup/doctor", summary="Doctor Signup", description="Create a new doctor account")
async def signup(credentials: Doctor):
    signup = doctor_signup(credentials)
    return signup

# SIGNUP ROUTE FOR PATIENT
@router.post("/signup/patient", summary="Patient Signup", description="Create a new patient account")
async def signup_patient(credentials: Patient):
    signup = patient_signup(credentials)
    return signup

# LOGIN ROUTE
@router.post("/login", description="Authenticate user with username and password")
async def login(credentials: LoginModel):
    login_route = login_user(credentials)
    return login_route