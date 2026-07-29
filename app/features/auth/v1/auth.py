from .doctor_signup import doctor_signup
from .patient_signup import patient_signup
from .login import login_patient, login_doctor
from core.auth import verify_token


async def signup_doctor_api(credentials):
    return await doctor_signup(credentials)


async def signup_patient_api(credentials):
    return await patient_signup(credentials)


async def doctor_login_api(credentials):
    return await login_doctor(credentials)

async def patient_login_api(credentials):
    return await login_patient(credentials)

def verify_token_api(token):
    return verify_token(token)
