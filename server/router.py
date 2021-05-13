from fastapi import APIRouter
from fastapi.responses import JSONResponse

from server.models import Challenge
from server.game import Game, games
from server.game import identifier, data_challenge
from server.websockets import notify_challenge_to_client
from server.connection_manager import manager
from server.redis import save_string

from server.constants import PREFIX_CHALLENGE

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    game = Game([challenge.challenger, challenge.challenged])
    games.append(game)
    challenge_id = identifier()
    save_string(
        PREFIX_CHALLENGE + challenge_id,
        data_challenge([challenge.challenger, challenge.challenged]),
    )
    await notify_challenge_to_client(
        challenge.challenged,
        challenge.challenger,
        challenge_id,
    )
    return challenge


@router.get("/users")
async def user_list():
    return JSONResponse({'users': list(manager.connections.keys())})
