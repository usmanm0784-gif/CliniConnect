from features.auth.auth_routes import router as auth_router
from features.doctors.doctor_routes import router as doctor_router
from features.Patients.patient_routes import router as patient_router
from fastapi import APIRouter

api_router = APIRouter()


# auth_router
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# doctor_router
api_router.include_router(doctor_router, prefix="/doctors", tags=["doctors"])

# patient_router
api_router.include_router(patient_router, prefix="/patients", tags=["patients"])