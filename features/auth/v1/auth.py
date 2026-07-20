from db_functions.auth import (
    get_user_by_email,
    create_user,
    create_doctor,
    create_patient
)

from datetime import timedelta
from fastapi import status
from logger import logger

from core.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
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

        if not doctor_result:
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
        if not patient_result:
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

async def login_user(credentials):
    try:
        # Find user
        user = await get_user_by_email(credentials.email)
        #print(user)
        if not user or not credentials.password == user["password"]:
            return api_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=0,
                message="wrong username or password",
            )
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"role": user["role"], "email": user["email"]},
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
        logger.error("error in login users")
        return api_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=0,
            message="An error occurred while logging in",
        )