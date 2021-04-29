import uuid
from typing import List


games = []


class Game:
    def __init__(
        self,
        players: List[str],
        challenge_id: str,
        name: str = 'quoridor'
    ):
        # to do: clean the challenge_id from web (not used)
        self.name = name
        self.players = players
        self.state = 'pending'
        self.game_id = None
        self.challenge_id = str(uuid.uuid4())
        self.turn_token = None

    def next_turn(self):
        self.turn_token = str(uuid.uuid4())
