from fastapi import APIRouter, Depends, BackgroundTasks
from models.doctor import AvailabilitySlot, DoctorUpdate
from core.auth import read_profile

from .v1.doctor import(
    get_all_doctors_api,
    get_doctors_by_specialization_api,
    update_doctor_profile_api,
    add_appointment_slots_api,
    remove_appointment_slots_api,
    get_all_appointment_slots_api,
    add_patient_notes_api,
    change_status_api
)

router = APIRouter()

# get all doctors
@router.get("/all", summary="Get All Doctors", description="Retrieve a list of all doctors")
async def get_all_doctors():
    return await get_all_doctors_api()
    
# get doctor by specialization
@router.get("/specialization", summary="Get Doctors by Specialization", description="Retrieve a list of doctors by specialization")
async def get_doctors_by_specialization(specialization: str):
    return await get_doctors_by_specialization_api(specialization)

# doctors can edit their profile and also can add experience
@router.put("/update/profile",summary="Update Doctor Profile")
async def update_doctor_profile(updated_data: DoctorUpdate,current_user: str = Depends(read_profile)):
    return await update_doctor_profile_api(updated_data, current_user)

@router.post("/add/appointment", summary="Add Appointment Slots")
async def add_appointment_slots(available_timings: list[AvailabilitySlot], current_user: dict = Depends(read_profile)):
    return await add_appointment_slots_api(available_timings, current_user)

# remove appointment slots
@router.delete("/remove/appointment", summary="Remove Appointment Slots")
async def remove_appointment_slots(slot_id: str,current_user: str = Depends(read_profile)):
    return await remove_appointment_slots_api(slot_id, current_user)

# get all appointment slots of doctor
@router.get("/appointments/all", summary="Get All Appointment Slots")
async def get_all_appointment_slots(doctor_email: str):
    return await get_all_appointment_slots_api(doctor_email)

@router.post("/add/patient_notes", summary="Add Notes to Patient Profile")
async def add_patient_notes(patient_email: str,notes: str,current_user: dict = Depends(read_profile)):
    return await add_patient_notes_api(patient_email, notes, current_user)
    
@router.put("/appointment/status", summary="Change appointment status")
async def change_status(appointment_status: str, slot_ID: str, background_tasks: BackgroundTasks, current_user: dict = Depends(read_profile),):
    return await change_status_api(appointment_status, slot_ID, current_user, background_tasks)