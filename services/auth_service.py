from repository.auth_repository import (
    get_user_by_email,
    create_user,
    create_doctor,
    create_patient
)
from datetime import timedelta
from logger import logger
from fastapi import HTTPException, status

from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, read_profile

def doctor_signup(credentials):

    existing_user = get_user_by_email(credentials.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    # Hash password here in the future
    user_result = create_user(credentials.email, credentials.password, "doctor")
    create_doctor(user_result.inserted_id, credentials)
    return {
        "message": "User created successfully",
        "user": {
            "title": credentials.title,
            "name": credentials.name,
            "phone_number": credentials.phone_number,
            "email": credentials.email
        }
    }

def patient_signup(credentials):

    # Check if user already exists
    existing_user = get_user_by_email(credentials.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    user_result = create_user(credentials.email, credentials.password, "patient")
    patient_id = user_result.inserted_id
    new_patient = {
        "name": credentials.name,
        "phone_number": credentials.phone_number,
        "email": credentials.email
    }
    create_patient(patient_id, new_patient)
    return {
        "message": "User created successfully",
        "user": {
            "name": credentials.name,
            "phone_number": credentials.phone_number,
            "email": credentials.email
        }
    }

def login_user(credentials):
    # Find user
    user = get_user_by_email(credentials.email)
    #print(user)
    if not user or not credentials.password == user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["role"], "email": user["email"]},
        expires_delta=access_token_expires
    )
    logger.info("Successful login")
    #print(read_profile(access_token))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": credentials.email
    }