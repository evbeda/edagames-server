import uuid
import json
from typing import List

from server.constants import (
    GAME_STATE_PENDING,
    DEFAULT_GAME,
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
        self.turn_token = None
        self.timer = None

    def next_turn(self):
        self.turn_token = str(uuid.uuid4())

    def to_JSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
        )


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
