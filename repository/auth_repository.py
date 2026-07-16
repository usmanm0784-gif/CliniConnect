from db import get_db_connection   
from pymongo.errors import PyMongoError
from fastapi import HTTPException

# Connect to database
db = get_db_connection()
users_collection = db["users"]  
patients_collection = db["patients"]  
doctors_collection = db["doctors"]

def get_user_by_email(email: str):
    try:
        existing_user = users_collection.find_one({"email": email})
        return existing_user
    
    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="error occurred could not get user"
        )

def create_user(email, password, role):
    try:
        user_result = users_collection.insert_one({
            "email": email,
            "password": password,
            "role": role
        })

        return user_result
    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="error occurred could not create a user"
        )    


def create_doctor(user_id, credentials):
    try:
        doctors_collection.insert_one({
            "_id": user_id,
            "title": credentials.title,
            "name": credentials.name,
            "phone_number": credentials.phone_number,
            "email": credentials.email,
            "city": credentials.city,
            "specialization": credentials.specialization
        })
    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="error occurred could not create a doctor"
        )

def create_patient(user_id, credentials):
    try:
        patients_collection.insert_one({
            "_id": user_id,
            "name": credentials.name,
            "phone_number": credentials.phone_number,
            "email": credentials.email
        })
    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="error occurred could not create a patient"
        )
        
    
