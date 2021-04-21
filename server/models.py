from pydantic import BaseModel


class Challenge(BaseModel):
    challenger: str
    challenged: str
