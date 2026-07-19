from db import get_db_connection   


# Connect to database
db = get_db_connection()
users_collection = db["users"]  
patients_collection = db["patients"]  
doctors_collection = db["doctors"]

async def get_user_by_email(email: str):

    existing_user = await users_collection.find_one({"email": email})

    return existing_user

async def create_user(email, password, role):

    user_result = await users_collection.insert_one({
        "email": email,
        "password": password,
        "role": role
    })

    return user_result

async def create_doctor(user_id, credentials):
    doctor_result = await doctors_collection.insert_one({
        "_id": user_id,
        "title": credentials.title,
        "name": credentials.name,
        "phone_number": credentials.phone_number,
        "email": credentials.email,
        "city": credentials.city,
        "specialization": credentials.specialization
    })

    return doctor_result.inserted_id

async def create_patient(user_id, credentials):
    patient_result = await patients_collection.insert_one({
        "_id": user_id,
        "name": credentials.name,
        "phone_number": credentials.phone_number,
        "email": credentials.email
    })

    return patient_result.inserted_id
    
