from fastapi import status
from logger import logger
from db_functions.doctor import get_doctor

from db_functions.patient import get_patient, add_notes
from utils.core_response import api_response


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
        result = await add_notes(patient_email, notes, doctor["email"])

        if result.modified_count == 0:
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