from db_functions.auth import (
    get_user_by_email,
    create_user,
    create_patient
)

from fastapi import status
from logger import logger

from utils.core_response import api_response

async def patient_signup(credentials):
    # Check if user already exists
    try:
        existing_user = await get_user_by_email(credentials.email)
        if existing_user:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="Email already exists",
            )
        user_result = await create_user(credentials.email, credentials.password, "patient")
        patient_id = user_result.inserted_id

        patient_result = await create_patient(patient_id, credentials)
        if not patient_result.inserted_id:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="could not create patient",
            )
        logger.info("Successful patient signup")

        return api_response(
            status_code= status.HTTP_201_CREATED,
            success=1,
            message= "patient created successfully",
            data= {
                "name" : credentials.name,
                "email": credentials.email
            }
        )

    except Exception as e:
        logger.error("error in signing up patients")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while creating patient account",
        )