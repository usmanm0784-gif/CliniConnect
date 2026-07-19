from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from auth import read_profile
from models.doctor import AvailabilitySlot
from logger import logger
from datetime import datetime
from db import get_db_connection
from .v1.confirmation_email import send_appointment_email

from .v1.patient import(
    appointment_booking
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

    appointments = list(slots_collection.find(
        {
            "patient_email": current_user["email"],
            "status": "booked"
        }
    ))

    for appointment in appointments:
        doctor = doctors_collection.find_one({"_id": appointment["doctor_id"]})
        appointment["doctor_name"] = doctor["name"] if doctor else "Unknown"

    logger.info(f"Appointments retrieved for patient {current_user['email']}")

    return {
        "appointments": [
            {
                "appointment_id": str(appointment["_id"]),
                "doctor_name": appointment.get("doctor_name", "Unknown"),
                "date": appointment["date"],
                "start_time": appointment["start_time"],
                "end_time": appointment["end_time"],
                "status": appointment["status"]
            }
            for appointment in appointments
        ]
    }