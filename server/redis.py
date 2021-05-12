import redis
from redis.exceptions import DataError
from uvicorn.config import logger

from .environment import REDIS_HOST, REDIS_LOCAL_PORT
from server.websockets import (
    notify_error_to_client,
    notify_feedback,
)

r = redis.Redis(host=REDIS_HOST, port=REDIS_LOCAL_PORT, db=0)


def save_string(key, value, expire=None):
    try:
        r.set(key, value, ex=expire)
    except DataError as e:
        logger.error(e)


async def get_string(key, client, caller='id'):
    try:
        data = r.get(key)
        r.delete(key)
        if data is None:
            await notify_feedback(
                client,
                f'{caller} not found',
            )
        return data
    except DataError as e:
        logger.error(e)
        await notify_error_to_client(
            client,
            f'DataError in {caller}, send a str',
        )
