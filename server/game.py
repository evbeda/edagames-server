import uuid
import json
from typing import List

from server.redis import save_string

from server.constants import DEFAULT_GAME


def identifier():
    return str(uuid.uuid4())


def next_turn(game_id):
    turn_token = identifier()
    save_string('t_' + game_id, turn_token)
    return turn_token


def data_challenge(
    players: List[str],
    name: str = DEFAULT_GAME,
):
    return json.dumps({
        'players': players,
        'game': name,
    })
