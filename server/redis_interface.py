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

redis_save_calls = {
    CHALLENGE_ID: save_string,
    TURN_TOKEN: save_string,
    BOARD_ID: save_string,
    LOG: append_to_stream,
}

redis_get_calls = {
    CHALLENGE_ID: get_string,
    TURN_TOKEN: get_string,
    BOARD_ID: get_string,
    # LOG: get_string,
}

relations = {
    CHALLENGE_ID: PREFIX_CHALLENGE,
    TURN_TOKEN: PREFIX_TURN_TOKEN,
    BOARD_ID: PREFIX_GAME,
    LOG: PREFIX_LOG,
}


def redis_save(key: str, value, caller: str):
    converted_key = key_conversion(key, caller)
    redis_save_calls[caller](converted_key, value)


async def redis_get(key: str, client: str, caller: str):
    converted_key = key_conversion(key, caller)
    if caller == LOG:
        #  get log not implemented yet
        pass
    else:
        data = get_string(converted_key)
        if data is None:
            pass
        elif data == -1:
            pass
    return data


def key_conversion(key: str, caller: str):
    prefix = relations.get(caller)
    return f'{prefix}{key}'
