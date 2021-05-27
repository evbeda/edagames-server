from server.constants import DEFAULT_GAME
from pydantic import BaseModel

from typing import List


class Challenge(BaseModel):
    challenger: str
    challenged: List[str]
    game_name: str = DEFAULT_GAME


class Tournament(BaseModel):
    tournament_id: str
    players: List[List[str]]
