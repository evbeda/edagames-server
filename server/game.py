import uuid
import json
from typing import List

from .redis import save_string

from server.constants import DEFAULT_GAME


def next_turn(game_id):
    turn_token = str(uuid.uuid4())
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


def identifier():
    return str(uuid.uuid4())
