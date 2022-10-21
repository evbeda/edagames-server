from server.exception import GameIdException
from server.constants import CLIENT_LIST, CLIENT_LIST_KEY, LOG, PLAIN_SEARCH
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from server.models import Challenge, Tournament
from server.utilities_server_event import make_challenge, make_tournament
from server.redis_interface import redis_get

router = APIRouter()


@router.post("/challenge")
async def challenge(challenge: Challenge):
    try:
        await make_challenge(
            challenge.challenger,
            challenge.challenged,
            challenge.game_name,
            challenge.debug_mode,
        )
        return challenge
    except Exception as e:
        message = f'Unhandled exception ocurred: {e}'
        status = 500

    return JSONResponse({
        'status': 'ERROR',
        'code': status,
        'message': message,
    }, status_code=status)


@router.post('/tournament')
async def tournament(tournament: Tournament):
    try:
        await make_tournament(
            tournament.tournament_id,
            tournament.challenges,
            tournament.game_name,
        )
    except Exception as e:
        message = f'Unhandled exception ocurred: {e}'
        status = 500
    else:
        return JSONResponse(tournament.json(), status_code=200)

    return JSONResponse({
        'status': 'ERROR',
        'code': status,
        'message': message,
    }, status_code=status)


@router.get("/users")
async def user_list():
    return JSONResponse({'users': await redis_get(CLIENT_LIST_KEY, CLIENT_LIST)})


@router.get('/match_details')
async def details(game_id: str, page_token: str = None):
    try:
        if not game_id:
            raise GameIdException('game_id should be a non-empty string')
        if not page_token or page_token == '-':
            moves, next_token = await redis_get(game_id, LOG)
            prev_token = None
        else:
            next_item, prev_token = await redis_get(page_token, PLAIN_SEARCH)
            moves, next_token = await redis_get(game_id, LOG, next_item=next_item)
    except GameIdException as e:
        message = e.message
        status = 400
    except Exception as e:
        message = f'Unhandled exception ocurred: {e}'
        status = 500
    else:
        # TODO: REMOVE
        [m.update({'current_player': 'player2' if i % 2 else 'player1'}) for i, m in enumerate(moves)]
        return JSONResponse({
            'details': list(moves),
            'prev': prev_token,
            'next': next_token,
        })

    return JSONResponse({
        'status': 'ERROR',
        'code': status,
        'message': message,
    }, status_code=status)
