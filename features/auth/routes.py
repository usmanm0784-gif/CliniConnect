from fastapi import APIRouter, Depends
from models.patient import Patient
from models.doctor import Doctor
from models.user import UserModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from .v1.auth import(
    signup_doctor_api,
    signup_patient_api,
    patient_login_api,
    doctor_login_api,
    verify_token_api
)


router = APIRouter()
security = HTTPBearer()

# SIGNUP ROUTE FOR DOCTOR
@router.post("/signup/doctor", summary="Doctor Signup", description="Create a new doctor account")
async def signup_doctor(credentials: Doctor):
    return await signup_doctor_api(credentials)


# SIGNUP ROUTE FOR PATIENT
@router.post("/signup/patient", summary="Patient Signup", description="Create a new patient account")
async def signup_patient(credentials: Patient):
    return await signup_patient_api(credentials)


# LOGIN ROUTE
@router.post("/login/doctor", description="Authenticate doctor with username and password")
async def login(credentials: UserModel):
    return await doctor_login_api(credentials)

# LOGIN ROUTE
@router.post("/login/patient", description="Authenticate patient with username and password")
async def login(credentials: UserModel):
    return await patient_login_api(credentials)


# verify token to get logout after 30 mins
@router.get("/verify-token")
async def verify_tokens(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_token_api(token)