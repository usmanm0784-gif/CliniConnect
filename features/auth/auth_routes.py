from fastapi import APIRouter, HTTPException, status
from pymongo.errors import PyMongoError
from models.SignupModel import SignupModelDoctor, SignupModelPatient
from models.LoginModel import LoginModel
from db import get_db_connection   
from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, read_profile
from datetime import timedelta
from logger import logger

router = APIRouter()

# Connect to database
db = get_db_connection()
users_collection = db["users"]  
patients_collection = db["patients"]  
doctors_collection = db["doctors"]  

# Simple password verification (plain text)
def verify_password(plain_password: str, stored_password: str) -> bool:
    return plain_password == stored_password

# SIGNUP ROUTE FOR DOCTOR
@router.post("/signup/doctor", status_code=status.HTTP_201_CREATED, summary="Doctor Signup", 
             description="Create a new doctor account")
async def signup(credentials: SignupModelDoctor):
    try:
        # Check if user already exists
        existing_user = users_collection.find_one({"email": credentials.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Store password as plain text
        new_user = {
            "title": credentials.title,
            "role": "doctor",
            "name": credentials.name,
            "phone_number": credentials.phone_number,
            "email": credentials.email,
            "city": credentials.city,
            "specialization": credentials.specialization,
            "password": credentials.password
        }

        # Insert new user into the database
        result = doctors_collection.insert_one(new_user)
        doctor_id = result.inserted_id
        # 6a54b7a2070b41ea6ceed9fc
        # 6a54b7a2070b41ea6ceed9fc
        users_collection.insert_one({"_id": doctor_id, "email": new_user["email"], "password": new_user["password"], "role": new_user["role"]})
        return {
            "message": "User created successfully",
            "user": {
                "title": credentials.title,
                "name": credentials.name,
                "phone_number": credentials.phone_number,
                "email": credentials.email
            }
        }

    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


# SIGNUP ROUTE FOR PATIENT
@router.post("/signup/patient", status_code=status.HTTP_201_CREATED, summary="Patient Signup",
              description="Create a new patient account")
async def signup_patient(credentials: SignupModelPatient):
    try:
        # Check if user already exists
        existing_user = users_collection.find_one({"email": credentials.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Store password as plain text
        new_user = {
            "role": "patient",
            "name": credentials.name,
            "phone_number": credentials.phone_number,
            "email": credentials.email,
            "password": credentials.password
        }

        # Insert new user into the database
        result = patients_collection.insert_one(new_user)
        patient_id = result.inserted_id
        users_collection.insert_one({"_id": patient_id, "email": new_user["email"], "password": new_user["password"], "role": new_user["role"]})

        return {
            "message": "User created successfully",
            "user": {
                "name": credentials.name,
                "phone_number": credentials.phone_number,
                "email": credentials.email
            }
        }

    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

# LOGIN ROUTE
@router.post("/login", status_code=status.HTTP_200_OK, summary="User Login",
              description="Authenticate user with username and password")
async def login(credentials: LoginModel):
    try:
        # Find user
        user = users_collection.find_one(
            {"email": credentials.email},
            {"_id": 0}
        )
        #print(user)
        if not user or not verify_password(credentials.password, user["password"]):
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
    except PyMongoError:
        logger.error("Database error during login")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")


