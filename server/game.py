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
    data = {
        'players': players,
        'accepted': [],
        'game': name,
    }
    if tournament_id:
        data.update({
            'tournament_id': tournament_id,
        })

    return json.dumps(data)
