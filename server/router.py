from fastapi import APIRouter
from .models import Challenge
from server.game import Game, games
import server.websockets
from .connection_manager import manager
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    game = Game([challenge.challenger, challenge.challenged], challenge.challenge_id)
    games.append(game)
    await server.websockets.notify_challenge_to_client(
        challenge.challenged,
        challenge.challenger,
        game.game_id,
    )
    return challenge


@router.get("/users")
async def user_list():
    return JSONResponse({'users': list(manager.connections.keys())})
