from datetime import datetime
from bson import ObjectId

from core.db import get_db_connection

# Connect to database
db = get_db_connection() 
slots_collection = db["slots"]
messages_collection = db["chat_messages"]


async def get_slot_by_id(slot_id: ObjectId):
    return await slots_collection.find_one({"_id": slot_id})


async def save_chat_message(slot_id: ObjectId, sender_email: str, sender_role: str, content: str):
    message = {
        "slot_id": slot_id,
        "sender_email": sender_email,
        "sender_role": sender_role,
        "content": content,
        "timestamp": datetime.utcnow(),
    }
    result = await messages_collection.insert_one(message)
    message["_id"] = result.inserted_id
    return message


async def get_chat_messages(slot_id: ObjectId):
    cursor = messages_collection.find({"slot_id": slot_id}).sort("timestamp", 1)
    return [msg async for msg in cursor]