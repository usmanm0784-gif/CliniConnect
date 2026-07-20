from .appointments import appointment_booking, fetch_appointments

async def book_appointment_api(appointment_data, doctor_email, background_tasks, current_user):
    return await appointment_booking(appointment_data, doctor_email, background_tasks, current_user)

async def view_my_appointments_api(current_user):
    return await fetch_appointments(current_user)