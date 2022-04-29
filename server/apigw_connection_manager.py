import asyncio
import json
import boto3
import jwt
from uvicorn.config import logger

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from uvicorn.config import logger

from server.connection_manager import ConnectionManager, AuthenticationError
from server.redis_interface import redis_delete, redis_get, redis_save

import server.constants as websocket_events
from server.constants import CLIENT_LIST, CLIENT_LIST_KEY
from .environment import JWT_TOKEN_KEY

from typing import Dict, List


class APIGatewayConnectionManager(ConnectionManager):
    client_id_to_bot: Dict
    bot_to_client_id: Dict

    def __init__(self):
        self.client_id_to_bot = {}
        self.bot_to_client_id = {}
        ConnectionManager.instance = self
        ConnectionManager.connection_type = 'api_gateway'
        self._client = boto3.client('apigatewaymanagementapi')

    async def connect(self, client_id: str, token: str):
        encoded_token = token.encode()
        try:
            user_to_connect = jwt.decode(
                encoded_token,
                JWT_TOKEN_KEY,
                algorithms=["HS256"],
            )
        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationError

        bot_name = user_to_connect.get('user')
        self.client_id_to_bot.update({
            client_id: bot_name
        })
        self.bot_to_client_id.update({
            bot_name: client_id
        })

        redis_save(CLIENT_LIST_KEY, bot_name, CLIENT_LIST)

        asyncio.create_task(self.notify_user_list_changed())

    async def disconnect(self, client_id: str):
        try:
            self._client.delete_connection(ConnectionId=client_id)
        except Exception as e:
            logger.info(f'Error while deleting client connection: {e}')

        try:
            del self.bot_to_client_id[self.client_id_to_bot[client_id]]
            del self.client_id_to_bot[client_id]
        except KeyError:
            logger.info(f'Client ({client_id}) not found')

    async def notify_user_list_changed(self):
        try:
            users = await redis_get(CLIENT_LIST_KEY, CLIENT_LIST)
        except Exception as e:
            logger.warning(f'Could not read user list from Redis: {e}')
            users = list(self.bot_to_client_id.keys())
        logger.info('[APIGateway] Users {}'.format(users))
        await self.broadcast(
            websocket_events.EVENT_LIST_USERS,
            {
                'users': users,
            },
        )

    async def broadcast(self, event: str, data: Dict):
        pass

    async def bulk_send(self, clients: List[str], event: str, data: Dict):
        pass

    async def send(self, client: str, event: str, data: Dict):
        pass

    async def _send(self):
        pass
