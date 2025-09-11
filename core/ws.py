from typing import Any

from fastapi import WebSocket

from core.unifiers import singleton


@singleton
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                await connection.send_text(message)

    async def send_task_updates(self, task: dict[str, Any], client_id: str):
        _ws_message: dict[str, str] = {"status": task["status"], "id": task["id"], "kind": task["kind"]}
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                await connection.send_json(_ws_message)


ws_manager = ConnectionManager()
