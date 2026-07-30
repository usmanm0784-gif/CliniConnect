from fastapi import status
from bson import ObjectId
from bson.errors import InvalidId
from logger import logger
from db_functions.doctor import get_slot, update_slot, get_doctor,get_doctor_by_id
from db_functions.patient import get_patient,get_patient_by_id
from db_functions.user import get_user_by_email

from .google_meet_service import create_google_meet
from utils.core_response import api_response
from .meet_email import send_appointment_meeting_email_doctor,send_appointment_meeting_email_patient


async def update_appointment_status(appointment_status, slot_ID, background_tasks, current_user):
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

        user_doctor = await get_user_by_email(current_user["email"])
        doctor = await get_doctor_by_id(user_doctor["_id"])
        
        user_patient = await get_user_by_email(slot["patient_email"])
        patient = await get_patient_by_id(user_patient["_id"])

        # Create Google Meet link when appointment is confirmed
        if appointment_status == "confirmed":

            # Do not create duplicate meeting
            if not slot.get("meeting_url"):

                meet_link = create_google_meet(slot["date"], slot["start_time"], slot["end_time"])
                update_data["meeting_url"] = meet_link



                # Email to patient
                background_tasks.add_task(
                    send_appointment_meeting_email_patient,
                    receiver_email=slot["patient_email"],
                    name=patient["name"],
                    doctor_name= doctor["name"],
                    patient_name=patient["name"],
                    appointment_date= slot["date"],
                    appointment_time=f"{slot["start_time"]} - {slot["end_time"]}",
                    appointment_link =  meet_link,
                )

                # Email to doctor
                background_tasks.add_task(
                    send_appointment_meeting_email_doctor,
                    receiver_email=slot["doctor_email"],
                    name=doctor["name"],
                    doctor_name= doctor["name"],
                    patient_name=patient["name"],
                    appointment_date= slot["date"],
                    appointment_time=f"{slot["start_time"]} - {slot["end_time"]}",
                    appointment_link =  meet_link,
                    title = doctor["title"],
                )

            else:
                update_data["meeting_url"] = slot["meeting_url"]


        # Update MongoDB
        result = await update_slot(m_slot_id, update_data)

        if result.modified_count == 0:
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
            message= f"An error occurred while updating appointment status: {e}"
        )
