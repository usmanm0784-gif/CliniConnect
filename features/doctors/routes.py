from fastapi import APIRouter, Depends
from db import get_db_connection   
from models.doctor import AvailabilitySlot, DoctorUpdate
from auth import read_profile

from .v1.doctor import(
    get_doctors,
    fetch_by_specialization,
    update_profile,
    add_appointment,
    remove_appointment,
    fetch_appointments,
    patient_notes,
    update_appointment_status
)

router = APIRouter()

# get all doctors
@router.get("/all", summary="Get All Doctors", description="Retrieve a list of all doctors")
async def get_all_doctors():
    return await get_doctors()
    
# get doctor by specialization
@router.get("/specialization", summary="Get Doctors by Specialization", description="Retrieve a list of doctors by specialization")
async def get_doctors_by_specialization(specialization: str):
    return await fetch_by_specialization(specialization)

# doctors can edit their profile and also can add experience
@router.put("/update/profile",summary="Update Doctor Profile")
async def update_doctor_profile(updated_data: DoctorUpdate,current_user: str = Depends(read_profile)):
    return await update_profile(updated_data, current_user)

@router.post("/add/appointment", summary="Add Appointment Slots")
async def add_appointment_slots(available_timings: list[AvailabilitySlot], current_user_role: dict = Depends(read_profile)):
    return await add_appointment(available_timings, current_user_role)

# remove appointment slots
@router.delete("/remove/appointment", summary="Remove Appointment Slots")
async def remove_appointment_slots(slot_id: str,current_user_role: str = Depends(read_profile)):
    return await remove_appointment(slot_id, current_user_role)

# get all appointment slots of doctor
@router.get("/appointments/all", summary="Get All Appointment Slots")
async def get_all_appointment_slots(doctor_email: str):
    return await fetch_appointments(doctor_email)

@router.post("/add/patient_notes", summary="Add Notes to Patient Profile")
async def add_patient_notes(patient_email: str,notes: str,current_user_role: dict = Depends(read_profile)):
    return await patient_notes(patient_email, notes, current_user_role)
    
@router.put("/appointment/status", summary="Change appointment status")
async def change_status(appointment_status: str, slot_ID: str, current_user_role: dict = Depends(read_profile)):
    return await update_appointment_status(appointment_status, slot_ID, current_user_role)