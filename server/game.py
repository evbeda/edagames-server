import uuid
from typing import List

from server.constants import GAME_STATE_PENDING

import threading

games = []


class Game:
    def __init__(
        self,
        players: List[str],
        challenge_id: str = None,
        name: str = 'quoridor'
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

    def set_timer(self, time, func):
        self.timer = threading.Timer(time, func)
