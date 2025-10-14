# websocket_manager.py
from collections import defaultdict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # room_id → список WebSocket-соединений
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, room_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: int, message: dict):
        """Отправить сообщение всем в комнате"""
        for connection in self.active_connections.get(room_id, []):
            await connection.send_json(message)

# Глобальный экземпляр
manager = ConnectionManager()