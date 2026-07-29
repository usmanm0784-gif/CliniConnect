from typing import Dict, List
from fastapi import WebSocket
from logger import logger


class ConnectionManager:
    """Tracks active websocket connections grouped by slot_id (the 'chat room')."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, slot_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(slot_id, []).append(websocket)

    def disconnect(self, slot_id: str, websocket: WebSocket):
        conns = self.active_connections.get(slot_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns and slot_id in self.active_connections:
            del self.active_connections[slot_id]

    async def broadcast(self, slot_id: str, message: dict):
        for connection in list(self.active_connections.get(slot_id, [])):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"broadcast to room {slot_id} failed: {e}")
                self.disconnect(slot_id, connection)

    async def close_room(self, slot_id: str, reason: str = "Session ended"):
        for connection in list(self.active_connections.get(slot_id, [])):
            try:
                await connection.close(code=1000, reason=reason)
            except RuntimeError:
                pass
        self.active_connections.pop(slot_id, None)


manager = ConnectionManager()