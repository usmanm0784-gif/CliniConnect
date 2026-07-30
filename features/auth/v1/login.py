from db_functions.user import (
    get_user_by_email
)

from datetime import timedelta
from fastapi import status
from logger import logger

from core.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password
from utils.core_response import api_response


async def login_doctor(credentials):
    role = "doctor"
    try:
        # Find user
        user = await get_user_by_email(credentials.email)
        if user:
            doctor_password = user.get("doctor_password")

            if not doctor_password:
                return api_response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    success=0,
                    message="doctor account does not exist"
                )
        #print(user)
        if not user or not verify_password(credentials.password, user["doctor_password"]):
            return api_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=0,
                message="wrong username or password",
            )
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"role": role, "email": user["email"]},
            expires_delta=access_token_expires
        )

        logger.info("Successful login")

        #print(read_profile(access_token))
        return api_response(
            status_code= status.HTTP_200_OK,
            success=1,
            message="user login successful",
            data= {
            "access_token": access_token,
            "token_type": "bearer",
            "email": credentials.email
            }
        )
    except Exception as e:
        logger.error(f"error in login users {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message=f"An error occurred while logging in: {e}"
        )


async def login_patient(credentials):
    role = "patient"
    try:
        # Find user
        user = await get_user_by_email(credentials.email)
        if user:
            patient_password = user.get("patient_password")

            if not patient_password:
                return api_response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    success=0,
                    message="Patient account does not exist"
                )

        if not user or not verify_password(credentials.password, user["patient_password"]):
            return api_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=0,
                message="wrong username or password",
            )
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"role": role, "email": user["email"]},
            expires_delta=access_token_expires
        )

        logger.info("Successful login")

        #print(read_profile(access_token))
        return api_response(
            status_code= status.HTTP_200_OK,
            success=1,
            message="user login successful",
            data= {
            "access_token": access_token,
            "token_type": "bearer",
            "email": credentials.email
            }
        )
    except Exception as e:
        logger.error(f"error in login users {e}")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message=f"An error occurred while logging in: {e}"
        )