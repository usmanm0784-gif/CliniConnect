from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from auth import read_profile
from models.doctor import AvailabilitySlot
from logger import logger
from datetime import datetime
from db import get_db_connection
from .v1.confirmation_email import send_appointment_email

from .v1.patient import(
    appointment_booking,
    fetch_appointments
)

router = APIRouter()

db = get_db_connection()
users_collection = db["users"]
slots_collection = db["slots"]
doctors_collection = db["doctors"]
patients_collection = db["patients"]

# patient can book appointment
@router.post("/book_appointment", summary="Book Appointment")
async def book_appointment(appointment_data: AvailabilitySlot, doctor_email: str,background_tasks: BackgroundTasks,
                           current_user: dict = Depends(read_profile)):
    return await appointment_booking(appointment_data, doctor_email, background_tasks, current_user)

# patient can view their appointments
@router.get("/my_appointments", summary="View My Appointments")
async def view_my_appointments(current_user: dict = Depends(read_profile)):
    return await fetch_appointments(current_user)