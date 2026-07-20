from fastapi import status
from bson import ObjectId
from bson.errors import InvalidId
from logger import logger
from db_functions.doctor import get_slot, update_slot, get_doctor
from db_functions.patient import get_patient

from .google_meet_service import create_google_meet
from utils.core_response import api_response

from .meet_email import send_appointment_meeting_email

async def update_appointment_status(appointment_status, slot_ID, current_user, background_tasks):
    try:
        if current_user["role"] != "doctor":
            return api_response(
                    status_code=status.HTTP_403_FORBIDDEN,
                    success=0,
                    message="Only doctors can change appointment status"
                )
        

        # Validate ObjectId
        try:
            m_slot_id = ObjectId(slot_ID)

        except InvalidId:
            return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=0,
                    message="Invalid appointment ID"
                )

        # Check appointment exists and belongs to doctor
        slot = await get_slot(m_slot_id, current_user["email"])

        if not slot:
            return api_response(
                    status_code=status.HTTP_404_NOT_FOUND,
                    success=0,
                    message="Appointment not found"
                )

        allowed_status = ["booked", "confirmed", "completed","cancelled"]

        if appointment_status not in allowed_status:
            return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=0,
                    message=f"Invalid status. Allowed values: {allowed_status}"
                )


        # Prevent unnecessary updates
        if slot["status"] == appointment_status:
            return api_response(
                success= 1,
                status_code= status.HTTP_200_OK,
                message="Appointment is already in this status.",
                data= {
                    "appointment_id": slot_ID,
                    "new_status": appointment_status,
                    "meeting_url": slot.get("meeting_url")
                }
            )


        update_data = {"status": appointment_status}

        doctor = await get_doctor(current_user["email"])
        patient = await get_patient(slot["patient_email"])

        # Create Google Meet link when appointment is confirmed
        if appointment_status == "confirmed":

            # Do not create duplicate meeting
            if not slot.get("meeting_url"):

                meet_link = create_google_meet(slot["date"], slot["start_time"], slot["end_time"])
                update_data["meeting_url"] = meet_link


                # receiver_email: str, name: str, doctor_name: str, patient_name: str, appointment_date: str,
                # appointment_time: str, appointment_id: str, appointment_link: str
                #email to both
                # Email to patient
                background_tasks.add_task(
                    send_appointment_meeting_email,
                    receiver_email=slot["patient_email"],
                    name=patient["name"],
                    doctor_name= doctor["name"],
                    patient_name=patient["name"],
                    appointment_date= slot["date"],
                    appointment_time=f"{slot["start_time"]} - {slot["end_time"]}",
                    appointment_id=str(slot["_id"]),
                    appointment_link =  meet_link,
                )

                # Email to doctor
                background_tasks.add_task(
                    send_appointment_meeting_email,
                    receiver_email=slot["doctor_email"],
                    name=doctor["name"],
                    doctor_name= doctor["name"],
                    patient_name=patient["name"],
                    appointment_date= slot["date"],
                    appointment_time=f"{slot["start_time"]} - {slot["end_time"]}",
                    appointment_id=str(slot["_id"]),
                    appointment_link =  meet_link,
                )

            else:
                update_data["meeting_url"] = slot["meeting_url"]


        # Update MongoDB
        result = await update_slot(m_slot_id, update_data)

        if result == 0:
            logger.error("Couldn't change appointment status")
            return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=0,
                    message="Unable to update appointment status"
                )
        return api_response(
                success= 1,
                status_code= status.HTTP_200_OK,
                message="Appointment status updated successfully",
                data= {
                    "appointment_id": slot_ID,
                    "new_status": appointment_status,
                    "meeting_url": update_data.get("meeting_url")
                }
            )
    except Exception as e:
        logger.error(f"updating appointment status failed: {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while updating appointment status",
            error_code="INTERNAL_SERVER_ERROR"
        )
