import os

# from server.constants import (
#     GAME_HOST_PORT,
#     GAME_PORT
# )


def load_env_var(name: str, default: str = None):
    var = os.environ.get(name, default)
    if var is None:
        raise EnvironmentError
    else:
        return var


JWT_TOKEN_KEY = load_env_var('SECRET_KEY_JWT', 'EDAGame$!2021')
WEB_SERVER_URL = load_env_var('WEB_SERVER_URL', 'localhost')
WEB_SERVER_PORT = load_env_var('WEB_SERVER_PORT', '8000')
REDIS_HOST = load_env_var('REDIS_HOST', 'localhost')
REDIS_LOCAL_PORT = load_env_var('REDIS_LOCAL_PORT', '6379')
REDIS_URL = load_env_var('REDIS_URL', '')
RABBIT_HOST = load_env_var('RABBIT_HOST', 'localhost')
RABBIT_PORT = load_env_var('RABBIT_PORT', '5672')

# Temporary?
GAME_HOST = load_env_var('GAME_HOST', 'localhost')
GAME_PORT = load_env_var('GAME_PORT', '50051')
# FAKE_SERVICE_DISCOVERY_GAME_HOST_PORT = load_env_var(GAME_HOST_PORT, GAME_PORT)
