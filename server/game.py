import uuid
import json
from typing import List

from server.redis import save_string

from server.constants import PREFIX_TURN_TOKEN


def identifier():
    return str(uuid.uuid4())


def next_turn(game_id):
    turn_token = identifier()
    save_string(f'{PREFIX_TURN_TOKEN}{game_id}', turn_token)
    return turn_token


def data_challenge(
    players: List[str],
    tournament_id: str,
    name: str,
):
    if tournament_id:
        data = {
            'players': players,
            'tournament_id': tournament_id,
            'game': name,
        }
    else:
        data = {
            'players': players,
            'game': name,
        }
    return json.dumps(data)
