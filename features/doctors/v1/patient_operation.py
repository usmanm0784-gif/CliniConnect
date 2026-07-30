from fastapi import status
from fastapi.encoders import jsonable_encoder
from logger import logger
from db_functions.doctor import get_doctor, get_doctor_by_id
from db_functions.user import get_user_by_email
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
        user = await get_user_by_email(current_user_role["email"])
        doctor = await get_doctor_by_id(user["_id"])

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
            error_code= f"{e}"
        )


async def fetch_patient(email, current_user_role):
    try:
        if current_user_role["role"] != "doctor":
            return api_response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=0,
                message="Only doctors can see patients"
            )
        patient = await get_patient(email)
        patient["_id"] = str(patient["_id"])
        if not patient:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=0,
                message= f"no patient found with email: {email}"
            )

        return api_response(
            status_code=status.HTTP_200_OK,
            success=1,
            message="found patient",
            data= jsonable_encoder(patient)
        )
    except Exception as e:
        logger.error(f"An error occurred while fetching patient {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while fetching patient",
            error_code= f"{e}"
        )