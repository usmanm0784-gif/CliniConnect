from fastapi import status
from logger import logger
from db_functions.doctor import(
    get_doctors_db,
    get_doctors_by_specialization,
    get_doctor,
    update_doctor_data,
)

from utils.core_response import api_response


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
        logger.error(f"while getting doctors failed: {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while getting doctors",
        )


async def fetch_by_specialization(specialization):
    try:
        doctors = await get_doctors_by_specialization(specialization)
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
        logger.error(f"while fetching doctors by specialization failed: {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message= f"An error occurred while fetching doctors by specialization {specialization}",
        )
    
    
async def update_profile(updated_data, current_user):
    try:
        #print(current_user)
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