from server.constants import DEFAULT_GAME
from pydantic import BaseModel

from typing import List


class Challenge(BaseModel):
    challenger: str
    challenged: List[str]
    game_name: str = DEFAULT_GAME


class Tournament(BaseModel):
    tournament_id: str
    challenges: List[List[str]]
    game_name: str = DEFAULT_GAME
