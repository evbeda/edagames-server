import redis

from .environment import REDIS_HOST, REDIS_LOCAL_PORT

redis = redis.Redis(host=REDIS_HOST, port=REDIS_LOCAL_PORT, db=0)
