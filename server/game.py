import uuid
import json
from typing import List

from .redis import save_string

from server.constants import (
    GAME_STATE_PENDING,
    DEFAULT_GAME,
    TIME_SLEEP
)


games = []


class Game:
    def __init__(
        self,
        players: List[str],
        name: str = DEFAULT_GAME
    ):
        # to do: clean the challenge_id from web (not used)
        self.name = name
        self.players = players
        self.state = GAME_STATE_PENDING
        self.game_id = None
        self.challenge_id = str(uuid.uuid4())
        self.timer = None

    def to_JSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
        )


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
