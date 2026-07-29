from fastapi import APIRouter,WebSocket,Depends
from core.auth import read_profile
from .v1.chat import chat_ws_api, get_messages_api

router = APIRouter()

@router.websocket("/ws/{slot_id}")
async def chat_ws(websocket: WebSocket, slot_id: str, token: str):
    return await chat_ws_api(websocket, slot_id, token)


@router.get("/{slot_id}/messages", summary="Get chat history for an appointment")
async def get_messages(slot_id: str, current_user: str= Depends(read_profile)):
    return await get_messages_api(slot_id, current_user)
