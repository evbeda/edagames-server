from server.constants import DEFAULT_GAME
from pydantic import BaseModel


class Challenge(BaseModel):
    challenger: str
    challenged: str
    tournament_id: str = None
    game_name: str = DEFAULT_GAME
