from db_functions.auth import (
    get_user_by_email,
    create_user,
    create_doctor
)

from fastapi import status
from logger import logger

from utils.core_response import api_response

async def doctor_signup(credentials):
    try:
        existing_user = await get_user_by_email(credentials.email)

        if existing_user:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="Email already exists",
            )

        # H
        user_result = await create_user(
            credentials.email,
            credentials.password,
            "doctor"
        )

        # create doctor is returning inserted id
        doctor_result = await create_doctor(user_result.inserted_id, credentials)

        if not doctor_result.inserted_id:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="could not create doctor",
            )
        logger.info("Successful doctor signup")
        
        return api_response(
            status_code=status.HTTP_201_CREATED,
            success=1,
            message="User created successfully",
            data={
                "title": credentials.title,
                "name": credentials.name,
                "phone_number": credentials.phone_number,
                "email": credentials.email,
            },
        )
    except Exception as e:
        logger.error("error in getting doctors signup")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while creating doctor account",
        )