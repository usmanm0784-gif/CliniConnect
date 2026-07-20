from fastapi import status
from bson import ObjectId
from bson.errors import InvalidId
from logger import logger
from fastapi.encoders import jsonable_encoder
from db_functions.doctor import(
    get_doctor,
    slot_conflict,
    create_slot,
    delete_slot,
    get_slots
)

from utils.core_response import api_response
async def add_slot(available_timings, current_user_role):
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
    
async def remove_slot(slot_id, current_user_role):
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

        if result.deleted_count == 0:
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
    
async def list_doctor_slots(email):
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