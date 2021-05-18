import json

from server.redis import (
    save_string,
    get_string,
    append_to_stream,
)

from server.constants import (
    CHALLENGE_ID,  # caller
    TURN_TOKEN,
    BOARD_ID,
    LOG,
    PREFIX_CHALLENGE,  # prefix
    PREFIX_TURN_TOKEN,
    PREFIX_GAME,
    PREFIX_LOG,
)


def redis_save(key, value, caller):
    pass


async def redis_get(key, caller):
    pass


def key_conversion(key, caller):
    relations = {
        CHALLENGE_ID: PREFIX_CHALLENGE,
        TURN_TOKEN: PREFIX_TURN_TOKEN,
        BOARD_ID: PREFIX_GAME,
        LOG: PREFIX_LOG,
    }
    return f'{relations.get(caller)}{key}'
