from fastapi import APIRouter
from .models import Challenge
from server.game import Game
from server.server import games, notify_challenge_to_client

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    game = Game(challenge.challenger, challenge.challenged)
    games.append(game)
    await notify_challenge_to_client(
        game.player,
        game.challenged_player,
        game.uuid_game,
    )
    return challenge
