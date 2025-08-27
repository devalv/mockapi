from typing import Any

from fastapi import WebSocket

from core.unifiers import singleton


@singleton
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, task: dict[str, Any]):
        _ws_message: dict[str, str] = {"status": task["status"], "id": task["id"]}
        for connection in self.active_connections:
            await connection.send_json(_ws_message)


ws_manager = ConnectionManager()
