import asyncio
from fastapi import WebSocket
import json
import jwt
from uvicorn.config import logger

from server.connection_manager import ConnectionManager
from server.redis_interface import redis_delete, redis_get, redis_save

import server.constants as websocket_events
from server.constants import CLIENT_LIST, CLIENT_LIST_KEY
from .environment import JWT_TOKEN_KEY

from typing import Dict, List


class ConnectionManagerWS(ConnectionManager):
    def __init__(self):
        self.connections = {}
        self.queue_manager = None
        ConnectionManager.instance = self

    def set_queue_manager(self, manager):
        self.queue_manager = manager

    async def connect(self, websocket: WebSocket, token: str):
        logger.info('Connection in progress!')
        encoded_token = token.encode()
        try:
            user_to_connect = jwt.decode(
                encoded_token,
                JWT_TOKEN_KEY,
                algorithms=["HS256"],
            )
        except jwt.exceptions.InvalidTokenError:
            logger.info('Invalid Token!')
            await websocket.close()
            return
        await websocket.accept()
        client = user_to_connect.get('user')
        logger.info(f'User connected {client}')

        self.connections[client] = websocket
        redis_save(CLIENT_LIST_KEY, client, CLIENT_LIST)
        # self.queue_manager.register_client(client)

        await self.notify_user_list_changed()
        return client

    async def broadcast(self, event: str, data: Dict):
        await self.bulk_send(self.connections.keys(), event, data)

    async def bulk_send(self, clients: List[str], event: str, data: Dict):
        for client in clients:
            try:
                asyncio.create_task(self._send(
                    self.connections[client],
                    event,
                    data,
                ))
            except KeyError:
                pass
                # self.queue_manager.send(client, event, data)

    async def send(self, client: str, event: str, data: Dict):
        try:
            await self._send(
                self.connections[client],
                event,
                data,
            )
        except KeyError:
            # self.queue_manager.send(client, event, data)
            pass

    async def _send(self, client_ws: WebSocket, event: str, data: Dict):
        logger.info(f'[Websocket] Send: Event: {event}, data: {data}')
        try:
            await client_ws.send_text(json.dumps({
                'event': event,
                'data': data,
            }))
        except Exception as e:
            logger.info(str(e))

    async def remove_user(self, user):
        try:
            # self.queue_manager.unregister_client(user)
            redis_delete(CLIENT_LIST_KEY, CLIENT_LIST, user)
            del self.connections[user]
            await self.notify_user_list_changed()
        except KeyError as e:
            logger.info('[Websocket]exception {}'.format(e))

    async def notify_user_list_changed(self):
        users = await redis_get(CLIENT_LIST_KEY, CLIENT_LIST)
        logger.info('[Websocket]Users {}'.format(users))
        await self.broadcast(
            websocket_events.EVENT_LIST_USERS,
            {
                'users': users,
            },
        )
