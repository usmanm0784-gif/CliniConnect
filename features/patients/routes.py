from fastapi import APIRouter, Depends, BackgroundTasks
from core.auth import read_profile
from models.doctor import AvailabilitySlot

from .v1.patient import(
    book_appointment_api,
    view_my_appointments_api
)

router = APIRouter()


# patient can book appointment
@router.post("/book/appointment", summary="Book Appointment")
async def book_appointment(appointment_data: AvailabilitySlot, doctor_email: str,background_tasks: BackgroundTasks,
                           current_user: dict = Depends(read_profile)):
    return await book_appointment_api(appointment_data, doctor_email, background_tasks, current_user)


# patient can view their appointments
@router.get("/appointments", summary="View My Appointments")
async def view_my_appointments(current_user: dict = Depends(read_profile)):
    return await view_my_appointments_api(current_user)