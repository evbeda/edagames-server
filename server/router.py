from fastapi import APIRouter
from fastapi.responses import JSONResponse

from server.models import Challenge
from server.game import identifier, data_challenge
from server.websockets import notify_challenge_to_client
from server.connection_manager import manager
from server.redis import save_string

from server.constants import PREFIX_CHALLENGE, TIME_CHALLENGE

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    challenge_id = identifier()
    save_string(
        f'{PREFIX_CHALLENGE}{challenge_id}',
        data_challenge([challenge.challenger, challenge.challenged]),
        TIME_CHALLENGE,
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
