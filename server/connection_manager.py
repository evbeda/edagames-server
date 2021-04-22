from fastapi import WebSocket
import json
import jwt
from .secrets import JWT_TOKEN_KEY

from typing import Dict


class ConnectionManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket, token: str):
        encoded_token = token.encode()
        try:
            user_to_connect = jwt.decode(
                encoded_token,
                JWT_TOKEN_KEY,
                algorithms=["HS256"],
            )
        except jwt.exceptions.InvalidTokenError:
            await websocket.close()
            return
        await websocket.accept()
        client = user_to_connect.get('user')
        self.connections[client] = websocket
        return client

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

    def remove_user(self, user):
        try:
            del self.connections[user]
        except KeyError:
            pass


manager = ConnectionManager()
