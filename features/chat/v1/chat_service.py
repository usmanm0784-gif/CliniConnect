import asyncio
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import WebSocket, WebSocketDisconnect, status
from fastapi.encoders import jsonable_encoder
from jose import JWTError, ExpiredSignatureError

from core.auth import verify_token
from core.config import AI_REPLY_WAIT_SECONDS
from logger import logger
from utils.core_response import api_response

from db_functions.chat import get_slot_by_id, save_chat_message, get_chat_messages
from .connection_manager import manager
from .chat_auth import user_belongs_to_slot, check_chat_status
from .ai_reply import generate_ai_reply

# If the doctor doesn't reply to a patient within this many seconds, the AI steps in.
AI_EMAIL = "ai-assistant"
AI_ROLE = "ai"

# room_id -> pending asyncio task waiting to send the AI message
pending_ai_timers: dict = {}


def cancel_ai_timer(room_id: str):
    task = pending_ai_timers.pop(room_id, None)
    if task:
        task.cancel()


async def send_ai_reply(room_id: str, m_slot_id: ObjectId):
    try:
        await asyncio.sleep(AI_REPLY_WAIT_SECONDS)
        history =await get_chat_messages(m_slot_id)
        chat_history = [{"role": m.get("sender_role"), "content": m.get("content")} for m in history]
        reply_text = await generate_ai_reply(chat_history)

        message = await save_chat_message(m_slot_id, AI_EMAIL, AI_ROLE, reply_text)
        await manager.broadcast(
            room_id,
            {
                "type": "message",
                "message_id": str(message["_id"]),
                "sender_email": AI_EMAIL,
                "sender_role": AI_ROLE,
                "content": reply_text,
                "timestamp": message["timestamp"].isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"send_ai_reply failed for room {room_id}: {e}")
    finally:
        pending_ai_timers.pop(room_id, None)


async def chat_service(websocket: WebSocket, slot_id: str, token: str):
    room_id = slot_id  # string form, used as the room key
    try:
        await manager.connect(room_id, websocket)
    except Exception as e:
        logger.error(f"could not connect to room {room_id}: {e}")
        return

    # auth
    try:
        payload = verify_token(token)
    except (JWTError, ExpiredSignatureError):
        await websocket.close(reason="could not authenticate user")
        return

    user_email = payload.get("email")
    user_role = payload.get("role")
    if not user_email:
        await websocket.close(reason="Invalid token payload")
        return

    # validate slot id
    try:
        m_slot_id = ObjectId(slot_id)
    except InvalidId:
        await websocket.close(reason="Invalid appointment ID")
        return
    
    slot = await get_slot_by_id(m_slot_id)
    if not slot:
        logger.error("slot not found in chat")
        await websocket.close(reason="Appointment not found")
        return
    
    # only the doctor/patient on this slot can join, and only while it's open
    if not user_belongs_to_slot(slot, user_email):
        await websocket.close(reason="You are not part of this appointment")
        return

    if not check_chat_status(slot["status"]):
        await websocket.close(reason="appointment status is not booked")
        return

    await manager.broadcast(
        room_id,
        {
            "type": "system",
            "content": f"{user_role} joined the chat",
            "timestamp": datetime.now().isoformat(),
        },
    )

    try:
        while True:
            data = await websocket.receive_json()
            content = (data.get("content") or "").strip()
            if not content:
                continue


            message = await save_chat_message(m_slot_id, user_email, user_role, content)

            await manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "message_id": str(message["_id"]),
                    "sender_email": user_email,
                    "sender_role": user_role,
                    "content": content,
                    "timestamp": message["timestamp"].isoformat(),
                },
            )

            # patient spoke -> start the 2 minute countdown for the doctor to reply
            # doctor spoke -> cancel any countdown, they've replied
            cancel_ai_timer(room_id)
            if user_role == "patient":
                pending_ai_timers[room_id] = asyncio.create_task(send_ai_reply(room_id, m_slot_id))
    except WebSocketDisconnect:
        cancel_ai_timer(room_id)
        manager.disconnect(room_id, websocket)
        await manager.broadcast(
            room_id,
            {
                "type": "system",
                "content": f"{user_role} left the chat",
                "timestamp": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"chat websocket error for slot {slot_id}: {e}")
        cancel_ai_timer(room_id)
        manager.disconnect(room_id, websocket)


async def messages(slot_id: str, current_user):
    try:
        m_slot_id = ObjectId(slot_id)
    except InvalidId:
        return api_response(status_code=status.HTTP_400_BAD_REQUEST, success=0, message="Invalid appointment ID")

    slot = await get_slot_by_id(m_slot_id)
    if not slot:
        return api_response(status_code=status.HTTP_404_NOT_FOUND, success=0, message="Appointment not found")

    if not user_belongs_to_slot(slot, current_user["email"]):
        return api_response(
            status_code=status.HTTP_403_FORBIDDEN,
            success=0,
            message="You are not part of this appointment",
        )

    chat_messages = await get_chat_messages(m_slot_id)
    for m in chat_messages:
        m["_id"] = str(m["_id"])
        m["slot_id"] = str(m["slot_id"])

    return api_response(
        success=1,
        status_code=status.HTTP_200_OK,
        message="fetched chat history successfully",
        data=jsonable_encoder(chat_messages),
    )