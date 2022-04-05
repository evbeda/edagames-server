from server.redis import (
    add_to_set,
    delete_key,
    get_set,
    remove_from_set,
    save_string,
    get_string,
    append_to_stream,
    get_stream,
)

from server.constants import (
    CHALLENGE_ID,  # caller
    CLIENT_LIST,
    TOKEN_EXPIRE,
    TURN_TOKEN,
    TOKEN_COMPARE,
    GAME_ID,
    LOG,
    LOG_EXPIRE,
    PREFIX_CHALLENGE,  # prefix
    PREFIX_TURN_TOKEN,
    PREFIX_GAME,
    PREFIX_LOG,
    EMPTY_PLAYER,  # web requests
    TIME_CHALLENGE,
    MSG_CHALLENGE,  # Feedback msgs
    MSG_TURN_TOKEN,
    MSG_TOKEN_COMPARE,
    MSG_GAME_ID,
    PLAIN_SEARCH,
)

expires_relation = {
    CHALLENGE_ID: TIME_CHALLENGE,
    TURN_TOKEN: TOKEN_EXPIRE,
}

relations = {
    CHALLENGE_ID: PREFIX_CHALLENGE,
    TURN_TOKEN: PREFIX_TURN_TOKEN,
    TOKEN_COMPARE: PREFIX_TURN_TOKEN,
    GAME_ID: PREFIX_GAME,
    LOG: PREFIX_LOG,
    PLAIN_SEARCH: '',
    CLIENT_LIST: '',
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
        CLIENT_LIST: add_to_set,
    }
    converted_key = key_conversion(key, caller)
    expire = expires_relation.get(caller, LOG_EXPIRE)
    redis_save_calls.get(caller, None)(converted_key, value, expire)


async def redis_get(key: str, caller: str, client: str = EMPTY_PLAYER, **kwargs):
    redis_get_calls = {
        CHALLENGE_ID: get_string,
        TURN_TOKEN: get_string,
        TOKEN_COMPARE: get_string,
        GAME_ID: get_string,
        LOG: get_stream,
        PLAIN_SEARCH: get_string,
        CLIENT_LIST: get_set,
    }
    converted_key = key_conversion(key, caller)
    data = redis_get_calls.get(caller)(converted_key, **kwargs)
    return data


def redis_delete(key: str, caller: str, value: str = None):
    redis_del_calls = {
        CLIENT_LIST: remove_from_set,
    }
    converted_key = key_conversion(key, caller)
    if value is not None:
        redis_del_calls.get(caller)(converted_key, value)
    else:
        delete_key(converted_key)


def key_conversion(key: str, caller: str):
    prefix = relations.get(caller)
    return f'{prefix}{key}'
