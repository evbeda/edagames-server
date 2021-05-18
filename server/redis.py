import json
import redis
from redis.exceptions import DataError
from uvicorn.config import logger

from .environment import REDIS_HOST, REDIS_LOCAL_PORT

from typing import Dict
from server.constants import REDIS_ERROR


r = redis.Redis(host=REDIS_HOST, port=REDIS_LOCAL_PORT, db=0, charset="utf-8", decode_responses=True)


def append_to_stream(key: str, data: Dict):
    try:
        parsed_data = {k: json.dumps(v) if type(v) == dict else v for k, v in data.items()}
        r.xadd(key, parsed_data)
    except TypeError as e:
        logger.error(f'Error while parsing data: {e}')
        return REDIS_ERROR
    except redis.RedisError as e:
        logger.error(f'Error while writing stream to Redis: {e}')
        return REDIS_ERROR


def save_string(key, value, expire=None):
    try:
        parsed_data = json.dumps(value)
        r.set(key, parsed_data, ex=expire)
    except DataError as e:
        logger.error(e)
        return REDIS_ERROR


async def get_string(key, client, caller='id'):
    try:
        data = r.get(key)
        parsed_data = json.loads(data)
        return parsed_data
    except DataError as e:
        logger.error(e)
        return REDIS_ERROR
