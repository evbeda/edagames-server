import asyncio
import json
import boto3
import jwt

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
        super().__init__()
        self.client_id_to_bot = {}
        self.bot_to_client_id = {}
        ConnectionManager.connection_type = 'api_gateway'
        self.client_id_to_apigw_url = {}
        self.all_boto3_clients = {}

    async def connect(self, apigw_url: str, client_id: str, token: str):
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

        self.client_id_to_apigw_url.update({
            client_id: apigw_url
        })

        redis_save(CLIENT_LIST_KEY, bot_name, CLIENT_LIST)

        await self.notify_user_list_changed()

    async def disconnect(self, client_id: str):
        try:
            boto3_client = self.get_boto3_client(client_id)
            boto3_client.delete_connection(ConnectionId=client_id)
        except Exception as e:
            logger.info(f'Error while deleting client connection: {e}')
        try:
            bot_name = self.client_id_to_bot[client_id]
            del self.bot_to_client_id[self.client_id_to_bot[client_id]]
        except KeyError:
            logger.info(f'Client ({client_id}) not found locally')
            return

        try:
            del self.client_id_to_apigw_url[client_id]
        except KeyError:
            logger.info(f'APIGW URL for Client ({client_id}) not found locally')
            return

        try:
            redis_delete(CLIENT_LIST_KEY, CLIENT_LIST, bot_name)
            del bot_name
            await self.notify_user_list_changed()
        except Exception as e:
            logger.error(f'Client ({self.client_id_to_bot[client_id]}) not found in Redis: {e}')

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
        await self.bulk_send(self.bot_to_client_id.keys(), event, data)

    async def bulk_send(self, clients: List[str], event: str, data: Dict):
        for client in clients:
            try:
                asyncio.create_task(self._send(
                    self.bot_to_client_id[client],
                    event,
                    data,
                ))
            except KeyError:
                pass

    async def send(self, client: str, event: str, data: Dict):
        try:
            await self._send(
                self.bot_to_client_id[client],
                event,
                data,
            )
        except KeyError:
            pass

    async def _send(self, client_apigw: str, event: str, data: Dict):
        logger.info(f'[APIGateway] Send: Event: {event}, data: {data}')
        try:
            boto3_client = self.get_boto3_client(client_apigw)
            boto3_client.post_to_connection(
                Data=json.dumps({
                    'event': event,
                    'data': data,
                }).encode(),
                ConnectionId=client_apigw
            )
        except Exception as e:
            # Remove "gone" clients
            if 'GoneException' in str(e):
                self.disconnect(client_apigw)
            logger.warning(f'[APIGateway] Error while sending message to client ({client_apigw}): {e}')

    def validate_client(self, client_apigw: str) -> bool:
        return client_apigw in self.client_id_to_bot.keys()

    def get_boto3_client(self, client_id: str) -> boto3.client:
        apigw_url = self.client_id_to_apigw_url[client_id]
        if apigw_url not in self.all_boto3_clients:
            self.all_boto3_clients[apigw_url] = boto3.client('apigatewaymanagementapi', endpoint_url=apigw_url)
        return self.all_boto3_clients[apigw_url]
