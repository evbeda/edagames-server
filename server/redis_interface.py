from server.redis import (
    save_string,
    get_string,
    append_to_stream,
)
from server.redis import (
    notify_feedback,
    notify_error_to_client,
)

from server.constants import (
    CHALLENGE_ID,  # caller
    TURN_TOKEN,
    TOKEN_COMPARE,
    BOARD_ID,
    LOG,
    PREFIX_CHALLENGE,  # prefix
    PREFIX_TURN_TOKEN,
    PREFIX_GAME,
    PREFIX_LOG,
    EMPTY_PLAYER,  # web requests
    REDIS_ERROR,  # error
    TIME_SLEEP,  # timers expire
    TIME_CHALLENGE,
)

redis_save_calls = {
    CHALLENGE_ID: save_string,
    TURN_TOKEN: save_string,
    BOARD_ID: save_string,
    LOG: append_to_stream,
}

expires_relation = {
    CHALLENGE_ID: TIME_CHALLENGE,
    TURN_TOKEN: TIME_SLEEP,
}

redis_get_calls = {
    CHALLENGE_ID: get_string,
    TURN_TOKEN: get_string,
    TOKEN_COMPARE: get_string,
    BOARD_ID: get_string,
    # LOG: get_string,
}

client_msgs = {
    CHALLENGE_ID: 'Not a challenge was found with the following id: ',
    TURN_TOKEN: 'Invalid turn token: ',
    TOKEN_COMPARE: 'Time limit: ',
    BOARD_ID: 'Invalid game id: ',
}

relations = {
    CHALLENGE_ID: PREFIX_CHALLENGE,
    TURN_TOKEN: PREFIX_TURN_TOKEN,
    TOKEN_COMPARE: PREFIX_TURN_TOKEN,
    BOARD_ID: PREFIX_GAME,
    LOG: PREFIX_LOG,
}


def redis_save(key: str, value, caller: str):
    converted_key = key_conversion(key, caller)
    expire = expires_relation.get(caller, None)
    redis_save_calls.get(caller, None)(converted_key, value, expire)


async def redis_get(key: str, caller: str, client: str = EMPTY_PLAYER):
    converted_key = key_conversion(key, caller)
    data = redis_get_calls.get(caller)(converted_key)
    if data is None:
        msg = client_msgs.get(caller)
        await notify_feedback(
            client,
            f'{msg}{key}',
        )
    elif data == REDIS_ERROR:
        await notify_error_to_client(
            client,
            f'DataError in {caller}, send a str',
        )
    return data


def key_conversion(key: str, caller: str):
    prefix = relations.get(caller)
    return f'{prefix}{key}'
