from core.db import get_db_connection   
from datetime import datetime

# Connect to database
db = get_db_connection() 
patients_collection = db["patients"]  
slots_collection = db["slots"]


async def get_patient(email):
    patient = await patients_collection.find_one({"email": email})
    return patient


async def add_notes(email, notes, doctor_email):
    # Update patient notes
    result = await patients_collection.update_one(
        {"email": email},
        {
            "$push": {
                "doctor_notes": {
                    "note": notes,
                    "doctor_email": doctor_email,
                    "created_at": datetime.utcnow()
                }
            }
        }
    )
    return result


async def get_appointments(email):

    appointments = await slots_collection.find(
        {
            "patient_email": email
        }
    ).to_list(length= None)

    return appointments

async def get_patient_phone_number(phone_number):
    patient = await patients_collection.find_one({"phone_number": phone_number})
    return patient

async def get_patient_by_id(id):
    patient = await patients_collection.find_one({"_id": id})
    return patient