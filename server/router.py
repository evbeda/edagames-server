from fastapi import APIRouter
from .models import Challenge
from server.game import Game, games
import server.websockets

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    game = Game(challenge.challenger, challenge.challenged)
    games.append(game)
    await server.websockets.notify_challenge_to_client(
        game.player,
        game.challenged_player,
        game.uuid_game,
    )
    return challenge
