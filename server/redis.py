import redis
from redis.exceptions import DataError
from uvicorn.config import logger

from .environment import REDIS_HOST, REDIS_LOCAL_PORT


r = redis.Redis(host=REDIS_HOST, port=REDIS_LOCAL_PORT, db=0)


def save_string(key, value, expire=None):
    try:
        r.set(key, value, ex=expire)
    except DataError as e:
        logger.error(e)
