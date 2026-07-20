from .profile import get_doctors, fetch_by_specialization, update_profile
from .slots import add_slot, remove_slot, list_doctor_slots
from .notes import add_notes
from .appointments import update_appointment_status

async def get_all_doctors_api():
    return await get_doctors()

async def get_doctors_by_specialization_api(specialization):
    return await fetch_by_specialization(specialization)
    
async def update_doctor_profile_api(updated_data, current_user):
    return await update_profile(updated_data, current_user)
    
async def add_appointment_slots_api(available_timings, current_user_role):
    return await add_slot(available_timings, current_user_role)
    
async def remove_appointment_slots_api(slot_id, current_user_role):
    return await remove_slot(slot_id, current_user_role)
    
async def get_all_appointment_slots_api(email):
    return await list_doctor_slots(email)
    
async def add_patient_notes_api(patient_email, notes ,current_user_role):
    return await add_notes(patient_email, notes ,current_user_role)
    
async def change_status_api(appointment_status, slot_ID, current_user_role, background_tasks):
    return await update_appointment_status(appointment_status, slot_ID, current_user_role, background_tasks)