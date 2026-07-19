from db import get_db_connection   
from datetime import datetime

# Connect to database
db = get_db_connection() 
patients_collection = db["patients"]  

async def get_patient(email):
    patient = await patients_collection.find_one({"email": email})
    return patient

async def add_notes(email, notes, doctor_email, datetime):
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
    return result.modified_count
