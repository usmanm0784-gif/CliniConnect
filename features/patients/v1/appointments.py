from logger import logger
from fastapi import status
from utils.core_response import api_response
from .confirmation_email import send_appointment_email

from db_functions.doctor import(
    get_doctor,
    get_availabe_slot,
    update_slot_status
)

from db_functions.patient import(
    get_patient,
    get_appointments
)

async def appointment_booking(appointment_data, doctor_email, background_tasks, current_user):
    try:
        if current_user["role"] != "patient":
            return api_response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=0,
                message="Only patients can book appointments"
            )

        # Check doctor exists
        doctor = await get_doctor(doctor_email)
        patient = await get_patient(current_user["email"])

        if not doctor:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message="Doctor not found"
            )

        date_str = appointment_data.date.isoformat()

        # Convert time to same format as database
        start_time = appointment_data.start_time.strftime("%H:%M:%S")
        end_time = appointment_data.end_time.strftime("%H:%M:%S")

        slot = await get_availabe_slot(doctor["_id"], appointment_data, start_time, end_time, status="available")
        # Find available slot

        if not slot or slot["status"] != "available":
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="This appointment slot is not available"
            )
        patient_email = current_user["email"]
        appointment_status="available"
        updated_status="booked"
        # Update slot status
        result = await update_slot_status(slot["_id"], appointment_status, updated_status, patient_email)

        if result == 0:
            logger.error("Failed to update slot status")
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="Unable to book appointment"
            )

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

        return api_response(
                status_code=status.HTTP_200_OK,
                success=1,
                message="appointment booking successful",
                data= {
                    "appointment_id": str(slot["_id"]),
                    "doctor": doctor_email,
                    "patient": current_user["email"],
                    "date": date_str,
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "booked"
                }
            )
    except Exception as e:
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while booking appointment",
        )

async def fetch_appointments(current_user):
    try:
        appointments = await get_appointments(current_user["email"], status="booked")
        if not appointments:
            return api_response(
                    status_code=status.HTTP_404_NOT_FOUND,
                    success=0,
                    message="no appointments found"
                )
        for appointment in appointments:
            doctor = await get_doctor(appointment["doctor_email"])
            appointment["doctor_name"] = doctor["name"] if doctor else "Unknown"

        logger.info(f"Appointments retrieved for patient {current_user['email']}")
        appointments_data = [
            {
                "appointment_id": str(appointment["_id"]),
                "doctor_name": appointment.get("doctor_name", "Unknown"),
                "doctor_email": appointment.get("doctor_email"),
                "date": appointment["date"],
                "start_time": appointment["start_time"],
                "end_time": appointment["end_time"],
                "status": appointment["status"]
            }
            for appointment in appointments
        ]

        return api_response(
                    status_code=status.HTTP_200_OK,
                    success=1,
                    message="fetching appointments successfully",
                    data= {
                        "appointments" : appointments_data
                    }
                )
    except Exception as e:
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while fetching appointments of patient",
        )