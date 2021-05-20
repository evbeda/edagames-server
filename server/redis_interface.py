from server.redis import (
    save_string,
    get_string,
    append_to_stream,
    get_stream,
)
from server.websockets import (
    notify_feedback,
    notify_error_to_client,
)

from server.constants import (
    CHALLENGE_ID,  # caller
    TURN_TOKEN,
    TOKEN_COMPARE,
    GAME_ID,
    LOG,
    PREFIX_CHALLENGE,  # prefix
    PREFIX_TURN_TOKEN,
    PREFIX_GAME,
    PREFIX_LOG,
    EMPTY_PLAYER,  # web requests
    REDIS_ERROR,  # error
    TIME_SLEEP,  # timers expire
    TIME_CHALLENGE,
    MSG_CHALLENGE,  # Feedback msgs
    MSG_TURN_TOKEN,
    MSG_TOKEN_COMPARE,
    MSG_GAME_ID,
    PLAIN_SEARCH,
)

expires_relation = {
    CHALLENGE_ID: TIME_CHALLENGE,
    TURN_TOKEN: TIME_SLEEP,
}

relations = {
    CHALLENGE_ID: PREFIX_CHALLENGE,
    TURN_TOKEN: PREFIX_TURN_TOKEN,
    TOKEN_COMPARE: PREFIX_TURN_TOKEN,
    GAME_ID: PREFIX_GAME,
    LOG: PREFIX_LOG,
    PLAIN_SEARCH: '',
}

client_msgs = {
    CHALLENGE_ID: MSG_CHALLENGE,
    TURN_TOKEN: MSG_TURN_TOKEN,
    TOKEN_COMPARE: MSG_TOKEN_COMPARE,
    GAME_ID: MSG_GAME_ID,
}


def redis_save(key: str, value, caller: str):
    redis_save_calls = {
        CHALLENGE_ID: save_string,
        TURN_TOKEN: save_string,
        GAME_ID: save_string,
        LOG: append_to_stream,
    }
    converted_key = key_conversion(key, caller)
    expire = expires_relation.get(caller, None)
    redis_save_calls.get(caller, None)(converted_key, value, expire)


async def redis_get(key: str, caller: str, client: str = EMPTY_PLAYER, **kwargs):
    redis_get_calls = {
        CHALLENGE_ID: get_string,
        TURN_TOKEN: get_string,
        TOKEN_COMPARE: get_string,
        GAME_ID: get_string,
        LOG: get_stream,
        PLAIN_SEARCH: get_string,
    }
    converted_key = key_conversion(key, caller)
    data = redis_get_calls.get(caller)(converted_key, **kwargs)
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
