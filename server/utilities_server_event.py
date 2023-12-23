from typing import (
    Dict,
    List,
)

import asyncio
from uvicorn.config import logger

from server.constants import (
    CHALLENGE_ID,
    CURRENT_PLAYER,
    DATA,
    DEBUG_AWAIT,
    DEBUG_MODE,
    EMPTY_PLAYER,
    GAME_ID,
    GAME_NAME,
    NORMAL_AWAIT,
    PLAYERS,
    TOKEN_COMPARE,
    TOURNAMENT_ID,
    TURN_TOKEN,
    TURN_DATA,
)
from server.exception import GameIdException
from server.game import (
    next_turn,
    identifier,
    data_challenge,
)
# from server.grpc_adapter import GRPCAdapterFactory
from server.redis_interface import (
    log_action,
    redis_save,
    redis_get,
)
from server.websockets import (
    notify_challenge_to_client,
    notify_your_turn,
    notify_error_to_client,
    notify_end_game_to_client,
)
from server.web_requests import (
    notify_end_game_to_web,
    create_game_to_game,
    penalize_to_game,
    abort_to_game,
)


async def move(
    data,
    game_name: str,
    debug_mode,
):
    token = await make_move(data)
    asyncio.create_task(
        make_penalize(
            data,
            game_name,
            token,
            debug_mode,
        )
    )


async def start_game(game_data: Dict):
    # adapter = await GRPCAdapterFactory.get_adapter(game_data.get(GAME_NAME))
    # data_received = await adapter.create_game(game_data.get(PLAYERS))
    game_created_data = await create_game_to_game(game_data.get(PLAYERS))
    redis_save(
        game_created_data.get(GAME_ID),
        game_data,
        GAME_ID,
    )
    await move(
        game_created_data,
        game_data.get(GAME_NAME),
        game_data.get(DEBUG_MODE),
    )


async def make_challenge(
    challenger,
    challenged,
    game_name,
    debug_mode=False,
):
    challenge_id = identifier()
    players = [challenger, *challenged]
    redis_save(
        challenge_id,
        data_challenge(
            players,
            [challenger],
            game_name,
            debug_mode,
        ),
        CHALLENGE_ID,
    )
    await notify_challenge_to_client(
        challenged,
        challenger,
        challenge_id,
    )


async def make_tournament(tournament_id: str, games: List[List[str]], game_name: str):
    for players in games:
        await start_game({
            'tournament_id': tournament_id,
            'players': players,
            'name': game_name,
            'debug_mode': False
        })


async def make_move(data):
    turn_token = next_turn(data[GAME_ID])
    turn_data = data[TURN_DATA]
    turn_data.update({
        TURN_TOKEN: turn_token,
        GAME_ID: data[GAME_ID],
    })
    await notify_your_turn(
        data[CURRENT_PLAYER],
        turn_data,
    )
    return turn_token


async def make_penalize(
    data,
    game_name,
    past_token,
    debug_mode,
):
    PENALIZE_AWAIT = DEBUG_AWAIT if debug_mode else NORMAL_AWAIT
    await asyncio.sleep(PENALIZE_AWAIT)
    token_valid = await redis_get(
        data[GAME_ID],
        TOKEN_COMPARE,
        data[CURRENT_PLAYER],
    )
    if token_valid == past_token:
        await log_action(
            data[GAME_ID],
            {
                'game_id': data[GAME_ID],
                'player': data[CURRENT_PLAYER],
                'event': 'timeout',
            },
        )
        # adapter = await GRPCAdapterFactory.get_adapter(game_name)
        # data_penalize = await adapter.penalize(data.game_id)
        data_penalize = await penalize_to_game(data[GAME_ID])
        if data_penalize[GAME_ID]:
            game_data = await redis_get(
                data_penalize[GAME_ID],
                GAME_ID,
            )
            if data_penalize[CURRENT_PLAYER] == EMPTY_PLAYER:
                await ServerEvent.game_over(data_penalize, game_data)
            else:
                await move(
                    data_penalize,
                    game_data.get(GAME_NAME),
                    debug_mode,
                )


def make_end_data_for_web(data):
    return [
        (value, data.get('score_' + key[7]))
        for key, value in data.items() if 'player_' in key
    ]


class ServerEvent:
    def __init__(self, response, client):
        self.response = response
        self.client = client

    async def search_value(self, value, default=None):
        try:
            value_search = self.response.get(DATA, {}).get(value, default)
        except Exception:
            logger.info(f'Value not found in message: {value}')
            value_search = None
        if value_search is None:
            await notify_error_to_client(
                self.client,
                str(GameIdException),
            )
        return value_search

    @classmethod
    async def game_over(cls, data, game: dict):
        next_turn(data[GAME_ID])
        end_data = make_end_data_for_web(data[TURN_DATA])
        data[TURN_DATA][GAME_ID] = data[GAME_ID]
        await notify_end_game_to_client(
            # game.get(PLAYERS),
            [
                data['play_data']['player_1'],
                data['play_data']['player_2'],
            ],
            data[TURN_DATA]
        )
        await notify_end_game_to_web(
            data[GAME_ID],
            game.get(TOURNAMENT_ID),
            end_data,
        )
