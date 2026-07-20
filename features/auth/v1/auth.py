from .doctor_signup import doctor_signup

from .patient_signup import patient_signup

from .login import login_user

async def signup_doctor_api(credentials):
    return await doctor_signup(credentials)

async def signup_patient_api(credentials):
    return await patient_signup(credentials)

async def login_api(credentials):
    return await login_user(credentials)