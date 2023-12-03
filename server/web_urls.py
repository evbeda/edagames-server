from .environment import (
    WEB_SERVER_URL,
    WEB_SERVER_PORT,
    GAME_HOST,
    GAME_PORT,
)

WEB_SERVER_FULL_URL = f'http://{WEB_SERVER_URL}:{WEB_SERVER_PORT}/match'
GAME_FULL_URL = f'http://{GAME_HOST}:{GAME_PORT}'
