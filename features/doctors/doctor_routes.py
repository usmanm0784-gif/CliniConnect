from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, status, Depends
from pymongo.errors import PyMongoError
from db import get_db_connection   
from models.doctor import AvailabilitySlot, Doctor, DoctorUpdate
from auth import read_profile
from logger import logger

from datetime import datetime
from .google_meet_service import create_google_meet
from .meet_email import send_appointment_email

# Connect to database
db = get_db_connection()
doctors_collection = db["doctors"]  
slots_collection = db["slots"]
patients_collection = db["patients"]

router = APIRouter()

# get all doctors
@router.get("/all", summary="Get All Doctors", description="Retrieve a list of all doctors")
async def get_all_doctors():
    try:
        doctors = list(doctors_collection.find({}, {"_id": 0}))
        return {"doctors": doctors}
    except PyMongoError:
        logger.error("Database error while retrieving doctors")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving doctors"
        )
    
# get doctor by specialization
@router.get("/specialization", summary="Get Doctors by Specialization", description="Retrieve a list of doctors by specialization")
async def get_doctors_by_specialization(specialization: str):
    try:
        doctors = list(doctors_collection.find({"specialization": specialization}, {"_id": 0}))
        if not doctors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No doctors found with specialization: {specialization}"
            )
        return {"doctors": doctors}
    except PyMongoError:
        logger.error("Database error while retrieving doctors by specialization")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving doctors"
        )
    

# doctors can edit their profile and also can add experience
@router.put("/update/profile",summary="Update Doctor Profile")
async def update_doctor_profile(updated_data: DoctorUpdate,current_user: str = Depends(read_profile)):
    try:

        if current_user["role"] != "doctor":
            raise HTTPException(
                status_code=403,
                detail="Only doctors can update profiles"
            )

        email = current_user["email"]

        doctor = doctors_collection.find_one({"email": email})

        if not doctor:
            raise HTTPException(status_code=404,detail="Doctor not found")

        doctors_collection.update_one(
            {
                "email": email
            },
            {
                "$set": updated_data.model_dump(exclude_none= True)
            }
        )

        logger.info("Doctor profile updated")

        return {"message": "Profile updated successfully"}

    except PyMongoError:
        logger.error("Database error while updating doctor profile")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/add/appointment", summary="Add Appointment Slots")
async def add_appointment_slots(available_timings: list[AvailabilitySlot], current_user_role: dict = Depends(read_profile)):
    try:
        if current_user_role["role"] != "doctor":
            raise HTTPException(status_code=403, detail="Only doctors can add appointment slots")
        
        doctor = doctors_collection.find_one(
            {
                "email": current_user_role["email"]
            }
        )

        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        for slot in available_timings:
            date_str = slot.date.isoformat()

            # Convert time to HH:MM:SS format
            start_time = slot.start_time.strftime("%H:%M:%S")
            end_time = slot.end_time.strftime("%H:%M:%S")


            # check conflict
            conflict = slots_collection.find_one(
                {
                    "doctor_id": doctor["_id"],
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


            if conflict:
                raise HTTPException(status_code=409, detail=f"Doctor already has slot {start_time}-{end_time}")

            slots_collection.insert_one(
                {
                    "doctor_id": doctor["_id"],
                    "doctor_email": doctor["email"],
                    "date": slot.date.isoformat(),
                    "start_time": slot.start_time.strftime("%H:%M:%S"),
                    "end_time": slot.end_time.strftime("%H:%M:%S"),
                    "status": "available"
                }
            )

        logger.info("Appointment slots added")

        return {"message": "Appointment slots added successfully"}

    except PyMongoError:
        logger.error("Database error while adding appointment slots")
        raise HTTPException(status_code=500, detail="Database error")

# remove appointment slots
@router.delete("/remove/appointment", summary="Remove Appointment Slots")
async def remove_appointment_slots(slot_id: str,current_user_role: str = Depends(read_profile)):
    try:
        if current_user_role["role"] != "doctor":
            raise HTTPException(
                status_code=403,
                detail="Only doctors can remove appointment slots"
            )
        try:
            slot_obj_id = ObjectId(slot_id)
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid slot ID"
            )

        doctor = doctors_collection.find_one({"email": current_user_role["email"]})

        if not doctor:
            raise HTTPException(status_code=404,detail="Doctor not found")

        result = slots_collection.delete_one({"_id": slot_obj_id, "doctor_id": doctor["_id"]})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Slot not found or you do not have permission to delete it")

        logger.info("Appointment slot removed")

        return {"message": "Appointment slot removed successfully"}
    except PyMongoError:
        logger.error("Database error while removing appointment slots")
        raise HTTPException(status_code=500, detail="Database error")
    

# get all appointment slots of doctor
@router.get("/appointments/all", summary="Get All Appointment Slots")
async def get_all_appointment_slots(doctor_email: str):
    try:
        doctor = doctors_collection.find_one({"email": doctor_email})

        if not doctor:
            raise HTTPException(status_code=404,detail="Doctor not found")

        slots = list(slots_collection.find({"doctor_id": doctor["_id"]},{"_id": 0}))
        # Convert ObjectId into string
        for slot in slots:
            slot["doctor_id"] = str(slot["doctor_id"])
        
        logger.info("Retrieved all appointment slots for doctor")

        return {"slots": slots}
    except PyMongoError:
        logger.error("Database error while retrieving appointment slots")
        raise HTTPException(status_code=500, detail="Database error")
    

@router.post("/add/patient_notes", summary="Add Notes to Patient Profile")
async def add_patient_notes(patient_email: str,notes: str,current_user_role: dict = Depends(read_profile)):
    try:
        if current_user_role["role"] != "doctor":
            raise HTTPException(
                status_code=403,
                detail="Only doctors can add notes to patient profiles"
            )

        doctor = doctors_collection.find_one({"email": current_user_role["email"]})

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )

        patient = patients_collection.find_one({"email": patient_email})

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Update patient notes
        result = patients_collection.update_one(
            {"email": patient_email},
            {
                "$push": {
                    "doctor_notes": {
                        "note": notes,
                        "doctor_email": doctor["email"],
                        "created_at": datetime.utcnow()
                    }
                }
            }
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Notes were not updated"
            )

        logger.info("Added notes to patient profile")

        return {
            "message": "Notes added to patient profile successfully"
        }

    except PyMongoError:
        logger.error("Database error while adding notes to patient profile")
        raise HTTPException(status_code=500, detail="Database error")
    
@router.put("/appointment/status", summary="Change appointment status")
async def change_status(appointment_status: str, slot_ID: str, current_user_role: dict = Depends(read_profile)):

    # Only doctor can change status
    if current_user_role["role"] != "doctor":
        raise HTTPException(
            status_code=403,
            detail="Only doctors can change appointment status"
        )

    # Validate ObjectId
    try:
        m_slot_id = ObjectId(slot_ID)

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid appointment ID")

    # Check appointment exists and belongs to doctor
    slot = slots_collection.find_one(
        {
            "_id": m_slot_id,
            "doctor_email": current_user_role["email"]
        }
    )


    if not slot:
        raise HTTPException(status_code=404, detail="Appointment not found")


    allowed_status = ["booked", "confirmed", "completed","cancelled"]

    if appointment_status not in allowed_status:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed values: {allowed_status}")


    # Prevent unnecessary updates
    if slot["status"] == appointment_status:
        return {
            "message": "Appointment is already in this status.",
            "appointment_id": slot_ID,
            "new_status": appointment_status,
            "meeting_url": slot.get("meeting_url")
        }


    update_data = {"status": appointment_status}

    # Create Google Meet link when appointment is confirmed
    if appointment_status == "confirmed":

        # Do not create duplicate meeting
        if not slot.get("meeting_url"):

            meet_link = create_google_meet(slot["date"], slot["start_time"], slot["end_time"])
            update_data["meeting_url"] = meet_link
        else:
            update_data["meeting_url"] = slot["meeting_url"]


    # Update MongoDB
    result = slots_collection.update_one(
        {
            "_id": m_slot_id
        },
        {
            "$set": update_data
        }
    )


    if result.modified_count == 0:
        logger.error("Couldn't change appointment status")
        raise HTTPException(status_code=400, detail="Unable to update appointment status")

    return {
        "message": "Appointment status updated successfully",
        "appointment_id": slot_ID,
        "new_status": appointment_status,
        "meeting_url": update_data.get("meeting_url")
    }