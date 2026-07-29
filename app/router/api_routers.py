from features.auth.routes import router as auth_router
from features.doctors.routes import router as doctor_router
from features.patients.routes import router as patient_router
from features.chat.routes import router as chat_router
from fastapi import APIRouter

api_router = APIRouter()


# auth_router
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])


# doctor_router
api_router.include_router(doctor_router, prefix="/doctors", tags=["doctors"])


# patient_router
api_router.include_router(patient_router, prefix="/patients", tags=["patients"])


# chat_router
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])