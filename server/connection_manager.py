from fastapi import WebSocket
import json
import jwt
from uvicorn.config import logger

import server.constants as websocket_events
from .environment import JWT_TOKEN_KEY

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
        await self.notify_user_list_changed()
        return client

    async def broadcast(self, data: Dict):
        for connection in self.connections.values():
            await connection.send_text(json.dumps(data))

    async def send(self, client: str, event: str, data: Dict):
        client_websocket = self.connections.get(client)
        logger.info('[Websocket]Send: Client : {} Event:{} ,data :{}'.format(client, event, data))
        if client_websocket is not None:
            await client_websocket.send_text(json.dumps({
                'event': event,
                'data': data,
            }))

    async def remove_user(self, user):
        try:
            del self.connections[user]
            await self.notify_user_list_changed()
        except KeyError as e:
            logger.info('[Websocket]exception {}'.format(e))

    async def notify_user_list_changed(self):
        data = {
            'event': websocket_events.EVENT_LIST_USERS,
            'data': {
                'users': list(self.connections.keys()),
            },
        }
        logger.info('[Websocket]Users {}'.format(list(self.connections.keys())))
        await self.broadcast(data)


manager = ConnectionManager()
