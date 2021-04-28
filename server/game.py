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
        self.name = name
        self.players = players
        self.uuid_game = str(uuid.uuid4())
        self.state = 'pending'
        self.challenge_id = challenge_id

    def next_turn(self):
        # Start timeout timer
        # Build turn_token
        # Return dict with turn_token
        return {'turn_token': '0000001'}
