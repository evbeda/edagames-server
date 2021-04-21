from fastapi import WebSocket
import json

from typing import Dict


class ConnectionManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket, client):
        await websocket.accept()
        self.connections[client] = websocket

    async def broadcast(self, data: str):
        for user, connection in self.connections.items():
            await connection.send_text(data)

    async def send(self, client: str, event: str, data: Dict[str, str]):
        client_websocket = self.connections.get(client)
        if client_websocket is not None:
            await client_websocket.send_text(json.dumps({
                'event': event,
                'data': data,
            }))


manager = ConnectionManager()
