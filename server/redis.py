import json
import redis
from hashlib import sha1
from redis.exceptions import DataError
from uvicorn.config import logger

from .environment import REDIS_HOST, REDIS_LOCAL_PORT

from typing import Dict
from server.constants import (
    LOG_EXPIRE,
    REDIS_ERROR,
    DEFAULT_EXPIRE,
    LOG_PAGE_SIZE,
)


redis_data = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_LOCAL_PORT,
    db=0,
    charset="utf-8",
    decode_responses=True,
)


def append_to_stream(key: str, data: Dict, expire: int = LOG_EXPIRE):
    try:
        parsed_data = {k: json.dumps(v) if type(v) == dict else v for k, v in data.items()}
        redis_data.xadd(key, parsed_data)
        redis_data.expire(key, expire)
    except TypeError as e:
        logger.error(f'Error while parsing data in append_to_stream: {e}')
    except redis.RedisError as e:
        logger.error(f'Error while writing stream to Redis: {e}')


def get_stream(key: str, next_item: str = '-'):
    try:
        data = redis_data.xrange(key, min=next_item, count=LOG_PAGE_SIZE + 1)
        if next_item != '-':
            next_prev_token = sha1(next_item.encode()).hexdigest()
        else:
            next_prev_token = None
        if len(data) > LOG_PAGE_SIZE:
            moves = dict(data[:-1]).values()
            next_item = data[-1][0]
            next_token = sha1(next_item.encode()).hexdigest()
            save_string(next_token, json.dumps((next_item, next_prev_token)))
        else:
            moves = dict(data).values()
            next_token = None
        return moves, next_token
    except redis.RedisError as e:
        logger.error(f'Error while reading stream from Redis: {e}')
        return [], ''


def save_string(key: str, value, expire: int = DEFAULT_EXPIRE):
    if type(value) != str:
        value = json.dumps(value)
    try:
        redis_data.set(key, value, ex=expire)
    except DataError as e:
        logger.error(f'Error while saving data in save_string: {e}')
        return REDIS_ERROR


def get_string(key: str):
    try:
        data = redis_data.get(key)
    except DataError as e:
        logger.error(f'Error while getting data from redis in get_string: {e}')
        return REDIS_ERROR
    if data is not None:
        try:
            parsed_data = json.loads(data)
            return parsed_data
        except json.decoder.JSONDecodeError:
            return data
    else:
        logger.info(f'{key} not found, most likely expired')
        return data


def add_to_set(key: str, value: str, _):
    try:
        return redis_data.sadd(key, value)
    except DataError as e:
        logger.error(f'Error while saving data in add_to_set: {e}')
        return REDIS_ERROR


def remove_from_set(key: str, value: str):
    try:
        return redis_data.srem(key, value)
    except DataError as e:
        logger.error(f'Error while deleting data in remove_from_set: {e}')
        return REDIS_ERROR


def get_set(key: str):
    try:
        redis_data.smembers(key)
    except DataError as e:
        logger.error(f'Error while getting data from redis in get_set: {e}')
        return REDIS_ERROR


def delete_key(key: str):
    try:
        return redis_data.delete(key)
    except DataError as e:
        logger.error(f'Error while removing key in delete_key: {e}')
        return REDIS_ERROR
