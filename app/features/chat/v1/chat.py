from .chat_service import messages, chat_service

async def chat_ws_api(websocket, slot_id, token):
    return await chat_service(websocket, slot_id, token)


async def get_messages_api(slot_id, current_user):
    return await messages(slot_id, current_user)