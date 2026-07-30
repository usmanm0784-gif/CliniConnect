
from core.config import ALLOWED_CHAT_STATUS


def user_belongs_to_slot(slot: dict, email: str) -> bool:
    # only the doctor and patient tied to this slot can access its chat
    return email in (slot.get("doctor_email"), slot.get("patient_email"))


def check_chat_status(status)-> bool:
    return status == ALLOWED_CHAT_STATUS
