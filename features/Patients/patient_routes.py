from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from auth import read_profile
from models.doctor import AvailabilitySlot
from logger import logger
from datetime import datetime
from db import get_db_connection
from .confirmation_email import send_appointment_email

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

    if current_user["role"] != "patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can book appointments"
        )

    # Check doctor exists
    doctor = doctors_collection.find_one({"email": doctor_email})

    patient = patients_collection.find_one({"email": current_user["email"]})

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")


    date_str = appointment_data.date.isoformat()

    # Convert time to same format as database
    start_time = appointment_data.start_time.strftime("%H:%M:%S")
    end_time = appointment_data.end_time.strftime("%H:%M:%S")


    # Find available slot
    slot = slots_collection.find_one(
        {
            "doctor_id": doctor["_id"],
            "date": appointment_data.date.isoformat(),
            "start_time": start_time,
            "end_time": end_time,
            "status": "available"
        }
    )


    if not slot or slot["status"] != "available":
        raise HTTPException(status_code=400, detail="This appointment slot is not available")


    # Update slot status
    result = slots_collection.update_one(
        {
            "_id": slot["_id"],
            "status": "available"
        },
        {
            "$set": {
                "status": "booked",
                "patient_email": current_user["email"],
                "booked_at": datetime.utcnow()
            }
        }
    )


    if result.modified_count == 0:
        logger.error("Failed to update slot status")
        raise HTTPException(status_code=400, detail="Unable to book appointment")

    # Email to patient
    background_tasks.add_task(
        send_appointment_email,
        receiver_email=current_user["email"],
        name=patient["name"],
        doctor_name=doctor["name"],
        patient_name=patient["name"],
        appointment_date=date_str,
        appointment_time=f"{start_time} - {end_time}",
        appointment_id=str(slot["_id"]),
    )

    # Email to doctor
    background_tasks.add_task(
        send_appointment_email,
        receiver_email=doctor["email"],
        name=doctor["name"],
        doctor_name=doctor["name"],
        patient_name=patient["name"],
        appointment_date=date_str,
        appointment_time=f"{start_time} - {end_time}",
        appointment_id=str(slot["_id"]),
    )
    logger.info(f"Appointment booked by {current_user['email']} with doctor {doctor_email}")


    return {
        "message": "Appointment booked successfully",
        "appointment_id": str(slot["_id"]),
        "doctor": doctor_email,
        "patient": current_user["email"],
        "date": date_str,
        "start_time": start_time,
        "end_time": end_time,
        "status": "booked"
    }

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