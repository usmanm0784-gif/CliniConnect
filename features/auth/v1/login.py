from db_functions.auth import (
    get_user_by_email
)

from datetime import timedelta
from fastapi import status
from logger import logger

from core.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from utils.core_response import api_response

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