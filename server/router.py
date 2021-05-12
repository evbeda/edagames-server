from fastapi import APIRouter
from fastapi.responses import JSONResponse

from server.models import Challenge
from server.game import Game, games
from server.websockets import notify_challenge_to_client
from server.connection_manager import manager
from server.redis import save_string

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    game = Game([challenge.challenger, challenge.challenged])
    games.append(game)
    save_string(game.challenge_id, game.to_JSON())
    await notify_challenge_to_client(
        challenge.challenged,
        challenge.challenger,
        game.challenge_id,
    )
    return challenge


@router.get("/users")
async def user_list():
    return JSONResponse({'users': list(manager.connections.keys())})
