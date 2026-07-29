from db_functions.user import (
    get_user_by_email,
    create_user_as_doctor,
    create_doctor,
    get_user_by_email_and_role,
    add_doctor_password
)
from db_functions.doctor import get_doctor_phone_number, get_doctor_by_id

from fastapi import status
from logger import logger
   
from core.auth import hash_password
from utils.core_response import api_response


async def doctor_signup(credentials):
    try:

        existing_user = await get_user_by_email(credentials.email)

        hashed_password = hash_password(credentials.password)

        existing_number = await get_doctor_phone_number(credentials.phone_number)
        if existing_number:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=0,
                message="this phone number already exists",
            )

        # User already exists (patient account exists)
        if existing_user:
            existing_doctor = await get_doctor_by_id(existing_user["_id"])
            if existing_doctor:
                return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=0,
                    message="doctor already exists",
                )

            # Add doctor password to existing user
            await add_doctor_password(
                existing_user["_id"],
                hashed_password
            )

            # Create doctor profile with same user id
            doctor_result = await create_doctor(
                existing_user["_id"],
                credentials
            )


            if not doctor_result.inserted_id:
                return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=0,
                    message="could not create doctor",
                )


        # New user signup
        else:
            user_id = await create_user_as_doctor(credentials.email, hashed_password)

            doctor_result = await create_doctor(user_id, credentials)


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
            message="Doctor created successfully",
            data={
                "title": credentials.title,
                "name": credentials.name,
                "phone_number": credentials.phone_number,
                "email": credentials.email,
            },
        )


    except Exception as e:
        logger.error(f"error in doctor signup {e}")

        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message=f"An error occurred while creating doctor account: {e}"
        )