from db_functions.user import (
    get_user_by_email,
    create_user_as_patient,
    create_patient,
    get_user_by_email_and_role,
    add_patient_password
)
from db_functions.patient import get_patient_phone_number,get_patient_by_id

from fastapi import status
from logger import logger

from utils.core_response import api_response
from core.auth import hash_password


async def patient_signup(credentials):
    try:

        existing_user = await get_user_by_email(credentials.email)

        hashed_password = hash_password(credentials.password)

        existing_number = await get_patient_phone_number(credentials.phone_number)
        if existing_number:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="this phone number already exists",
            )


        # User already exists (doctor account exists)
        if existing_user:

            existing_patient = await get_patient_by_id(existing_user["_id"])

            if existing_patient:
                return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=0,
                    message="patient already exists",
                )


            # Add patient password to existing user
            await add_patient_password(
                existing_user["_id"],
                hashed_password
            )


            # Create patient profile using same user id
            patient_result = await create_patient(
                existing_user["_id"],
                credentials
            )


            if not patient_result.inserted_id:
                return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=0,
                    message="could not create patient",
                )


        # New patient signup
        else:

            user_result = await create_user_as_patient(
                credentials.email,
                hashed_password
            )


            patient_result = await create_patient(
                user_result.inserted_id,
                credentials
            )


            if not patient_result.inserted_id:
                return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=0,
                    message="could not create patient",
                )


        logger.info("Successful patient signup")


        return api_response(
            status_code=status.HTTP_201_CREATED,
            success=1,
            message="patient created successfully",
            data={
                "name": credentials.name,
                "email": credentials.email
            }
        )


    except Exception as e:
        logger.error(f"error in signing up patients {e}")

        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message=f"An error occurred while creating patient account: {e}"
        )