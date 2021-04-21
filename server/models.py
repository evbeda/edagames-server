from pydantic import BaseModel


class Challenge(BaseModel):
    challenger: str
    challenged: str
    challenge_id: str
