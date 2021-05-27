from server.exception import GameIdException
from server.constants import LOG, PLAIN_SEARCH
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from server.models import Challenge
from server.connection_manager import manager
from server.utilities_server_event import make_challenge
from server.redis_interface import redis_get

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    await make_challenge([challenge.challenger, challenge.challenged])
    return challenge


@router.get("/users")
async def user_list():
    return JSONResponse({'users': list(manager.connections.keys())})


@router.get('/match_details')
async def details(game_id: str, continuation_token: str = None):
    try:
        if not game_id:
            raise GameIdException('game_id should be a non-empty string')
        if continuation_token:
            next_item = await redis_get(continuation_token, PLAIN_SEARCH)
            moves, token = await redis_get(game_id, LOG, next_item=next_item)
        else:
            moves, token = await redis_get(game_id)
    except GameIdException as e:
        message = e.message
        status = 400
    except Exception as e:
        message = f'Unhandled exception ocurred: {e}'
        status = 500
    else:
        return JSONResponse({
            'details': moves,
            'continuation_token': token,
        })

    return JSONResponse({
        'status': 'ERROR',
        'code': status,
        'message': message,
    }, status_code=status)
