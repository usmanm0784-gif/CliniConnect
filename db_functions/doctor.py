from core.db import get_db_connection
from datetime import datetime

# Connect to database
db = get_db_connection() 
doctors_collection = db["doctors"]
slots_collection = db["slots"]


async def get_doctors_db():
    doctors = await doctors_collection.find({}, {"_id": 0}).to_list(length=None)
    return doctors


async def get_doctors_by_specialization(specialization):
    doctors = await doctors_collection.find({"specialization": specialization}, {"_id": 0}).to_list(length=None)
    return doctors


async def get_doctor(email):
    doctor = await doctors_collection.find_one({"email": email})
    return doctor


async def update_doctor_data(updated_data, email):

    update = await doctors_collection.update_one(
        {
            "email": email
        },
        {
            "$set": updated_data.model_dump(exclude_none= True)
        }
    )

    return update


async def slot_conflict(doctor_id, date_str, start_time, end_time):
    conflict = await slots_collection.find_one(
        {
            "doctor_id": doctor_id,
            "date": date_str,      
            "$or": [
                {
                    "start_time": {"$lt": end_time},
                    "end_time": {"$gt": start_time}
                }
            ],     
            "status": {
                "$ne": "cancelled"
            }
        }
    )
    return conflict


async def create_slot(doctor_id, doctor_email, date, start_time, end_time, status= "available"):
    slot = await slots_collection.insert_one(
        {
            "doctor_id": doctor_id,
            "doctor_email": doctor_email,
            "date": date.isoformat(),
            "start_time": start_time.strftime("%H:%M:%S"),
            "end_time": end_time.strftime("%H:%M:%S"),
            "status": status
        }
    )
    return slot


async def delete_slot(slot_obj_id, doctor_id):
    result = await slots_collection.delete_one({"_id": slot_obj_id, "doctor_id": doctor_id})
    return result


async def get_slots(doctor_id):
    slots = await slots_collection.find({"doctor_id": doctor_id},{"_id": 0}).to_list(length=None)
    return slots


async def get_slot(m_slot_id, email):
    slot = await slots_collection.find_one(
        {
            "_id": m_slot_id,
            "doctor_email": email
        }
    )
    return slot


async def update_slot(m_slot_id, update_data):
    result = await slots_collection.update_one(
        {
            "_id": m_slot_id
        },
        {
            "$set": update_data
        }
    )
    return result


async def get_availabe_slot(doctor_id, appointment_data, start_time, end_time, status= "available"):
    # Find available slot
    slot = await slots_collection.find_one(
        {
            "doctor_id": doctor_id,
            "date": appointment_data.date.isoformat(),
            "start_time": start_time,
            "end_time": end_time,
            "status": status
        }
    )
    return slot


async def update_slot_status(slot_id, status, updated_status, email):
    # Update slot status
    result = await slots_collection.update_one(
        {
            "_id": slot_id,
            "status": status
        },
        {
            "$set": {
                "status": updated_status,
                "patient_email": email,
                "booked_at": datetime.utcnow()
            }
        }
    )
    return result