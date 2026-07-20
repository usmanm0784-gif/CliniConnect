from fastapi import status
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from logger import logger
from fastapi.encoders import jsonable_encoder
from db_functions.doctor import(
    get_doctors_db,
    get_doctors_by_specialization_db,
    get_doctor,
    update_doctor_data,
    slot_conflict,
    create_slot,
    delete_slot,
    get_slots,
    get_slot,
    update_slot
)
from db_functions.patient import(
    get_patient,
    add_notes
)

from .google_meet_service import create_google_meet
from core_response.response import api_response

async def get_doctors():
    try:
        doctors = await get_doctors_db()
        if not doctors:
            return api_response(
                status_code = status.HTTP_400_BAD_REQUEST,
                success = 0,
                message="could not get doctors"
            )
        return api_response(
            status_code=status.HTTP_200_OK,
            success=1,
            message="get all doctors",
            data=doctors,
        )
    except Exception as e:
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while getting doctors",
        )

async def fetch_by_specialization(specialization):
    try:
        doctors = await get_doctors_by_specialization_db(specialization)
        #print(doctors)
        if not doctors:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message= f"could not find doctors with {specialization}"
            )
        return api_response(
            status_code= status.HTTP_200_OK,
            success=1,
            message= f"doctors with specialization {specialization}",
            data=doctors
        )
    except Exception as e:
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message= f"An error occurred while fetching doctors by specialization {specialization}",
        )
    
async def update_profile(updated_data, current_user):
    try:
        print(current_user)
        if current_user["role"] != "doctor":
            return api_response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=0,
                message="Only doctors can update profile",
                error_code="ACCESS_DENIED"
            )

        email = current_user["email"]

        doctor = await get_doctor(email)

        if not doctor:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message="Doctor not found",
                error_code="DOCTOR_NOT_FOUND"
            )

        result = await update_doctor_data(updated_data, email)

        if result.modified_count == 0:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="No changes made",
                error_code="NO_UPDATE"
            )

        logger.info("Doctor profile updated")

        return api_response(
            status_code=status.HTTP_200_OK,
            success=1,
            message="Doctor profile updated successfully",
        )

    except Exception as e:
        logger.error(f"Doctor profile update failed: {e}")

        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while updating doctor profile",
            error_code="INTERNAL_SERVER_ERROR"
        )
    
async def add_appointment(available_timings, current_user_role):
    try:
        if current_user_role["role"] != "doctor":
            return api_response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=0,
                message="Only doctors can add appointment slots",
                error_code="ACCESS_DENIED"
            )
        doctor = await get_doctor(current_user_role["email"])


        if not doctor:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message="doctor not found"
            )

        for slot in available_timings:
            date_str = slot.date.isoformat()

            # Convert time to HH:MM:SS format
            start_time = slot.start_time.strftime("%H:%M:%S")
            end_time = slot.end_time.strftime("%H:%M:%S")
            doctor_id = doctor["_id"]

            # check conflict
            conflict = await slot_conflict(doctor_id, date_str, start_time, end_time)

            if conflict:
                return api_response(
                    status_code=status.HTTP_409_CONFLICT,
                    success=0,
                    message= f"Doctor already has slot {start_time}-{end_time}"
                )
            await create_slot(doctor_id, doctor["email"], slot.date, slot.start_time, slot.end_time, status= "available")

        logger.info("Appointment slots added")

        return api_response(
            success= 1,
            status_code= status.HTTP_201_CREATED,
            message="slot created successfuly"
        )
    except Exception as e:
        logger.error(f"adding appointment failed: {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while adding appointment",
            error_code="INTERNAL_SERVER_ERROR"
        )
    
async def remove_appointment(slot_id, current_user_role):
    try:
        if current_user_role["role"] != "doctor":
            return api_response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=0,
                message="Only doctors can remove appointment slots",
                error_code="ACCESS_DENIED"
            )
        try:
            slot_obj_id = ObjectId(slot_id)
        except InvalidId:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="Invalid slot ID"
            )

        doctor = await get_doctor(current_user_role["email"])

        if not doctor:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message="Doctor not found"
            )

        result = await delete_slot(slot_obj_id, doctor["_id"])

        if result == 0:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message="Slot not found or you do not have permission to delete it"
            )

        logger.info("Appointment slot removed")

        return api_response(
            success= 1,
            status_code= status.HTTP_201_CREATED,
            message="slot removed successfuly"
        )
    except Exception as e:
        logger.error(f"removing appointment failed: {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while removing appointment slots",
            error_code="INTERNAL_SERVER_ERROR"
        )
    
async def fetch_appointments(email):
    try:
        doctor = await get_doctor(email)
        if not doctor:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message="Doctor not found"
            )

        slots = await get_slots(doctor["_id"])
        #print(slots)
        # Convert ObjectId into string
        for slot in slots:
            slot["doctor_id"] = str(slot["doctor_id"])
        
        logger.info("Retrieved all appointment slots for doctor")

        return api_response(
            success= 1,
            status_code= status.HTTP_200_OK,
            message="fetched all slots successfuly",
            data = jsonable_encoder(slots)
        )
    except Exception as e:
        logger.error(f"fetching appointments failed: {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while fetching appointments",
            error_code="INTERNAL_SERVER_ERROR"
        )
    
async def patient_notes(patient_email, notes ,current_user_role):
    try:
        if current_user_role["role"] != "doctor":
            return api_response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=0,
                message="Only doctors can add notes to patient profiles"
            )

        doctor = await get_doctor(current_user_role["email"])

        if not doctor:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message="Doctor not found"
            )

        patient = await get_patient(patient_email)

        if not patient:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message="Patient not found"
            )

        # Update patient notes
        result = await add_notes(patient_email, notes, doctor["email"], datetime)

        if result == 0:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="Notes were not updated"
            )
        logger.info("Added notes to patient profile")

        return api_response(
            success= 1,
            status_code= status.HTTP_200_OK,
            message="added notes successfuly",
        )
    except Exception as e:
        logger.error(f"adding notes to patient profile failed: {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while adding notes to patient profile",
            error_code="INTERNAL_SERVER_ERROR"
        )
    
async def update_appointment_status(appointment_status, slot_ID, current_user_role):

    if current_user_role["role"] != "doctor":
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
    slot = await get_slot(m_slot_id, current_user_role["email"])

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

    # Create Google Meet link when appointment is confirmed
    if appointment_status == "confirmed":

        # Do not create duplicate meeting
        if not slot.get("meeting_url"):

            meet_link = create_google_meet(slot["date"], slot["start_time"], slot["end_time"])
            update_data["meeting_url"] = meet_link
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
