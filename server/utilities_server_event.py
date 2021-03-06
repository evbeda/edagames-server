import asyncio
from uvicorn.config import logger

from server.game import next_turn, identifier, data_challenge
from server.redis_interface import (
    log_action,
    redis_save,
    redis_get,
)
from server.grpc_adapter import GRPCAdapterFactory
from server.exception import GameIdException
from server.websockets import (
    notify_challenge_to_client,
    notify_your_turn,
    notify_error_to_client,
    notify_end_game_to_client,
)
from server.web_requests import notify_end_game_to_web

from typing import Dict, List
from server.constants import (
    GAME_NAME,
    TIME_SLEEP,
    TOURNAMENT_ID,
    TURN_TOKEN,
    GAME_ID,
    DATA,
    PLAYERS,
    CHALLENGE_ID,
    TOKEN_COMPARE,
    EMPTY_PLAYER,
)


async def move(data, game_name: str):
    token = await make_move(data)
    asyncio.create_task(make_penalize(data, game_name, token))


async def start_game(game_data: Dict):
    adapter = await GRPCAdapterFactory.get_adapter(game_data.get(GAME_NAME))
    data_received = await adapter.create_game(game_data.get(PLAYERS))
    redis_save(
        data_received.game_id,
        game_data,
        GAME_ID,
    )
    await move(data_received, game_data.get(GAME_NAME))


async def make_challenge(challenger, challenged, game_name):
    challenge_id = identifier()
    players = [challenger, *challenged]
    redis_save(
        challenge_id,
        data_challenge(players, [challenger], game_name),
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
        })


async def make_move(data):
    turn_token = next_turn(data.game_id)
    data.turn_data.update({
        TURN_TOKEN: turn_token,
        GAME_ID: data.game_id,
    })
    await notify_your_turn(
        data.current_player,
        data.turn_data,
    )
    return turn_token


async def make_penalize(data, game_name, past_token):
    await asyncio.sleep(TIME_SLEEP)
    token_valid = await redis_get(
        data.game_id,
        TOKEN_COMPARE,
        data.current_player,
    )
    if token_valid == past_token:
        await log_action(
            data.game_id,
            {
                'game_id': data.game_id,
                'player': data.current_player,
                'event': 'timeout',
            },
        )
        adapter = await GRPCAdapterFactory.get_adapter(game_name)
        data_penalize = await adapter.penalize(data.game_id)
        if data_penalize.game_id:
            game_data = await redis_get(
                data_penalize.game_id,
                GAME_ID,
            )
            if data_penalize.current_player == EMPTY_PLAYER:
                await ServerEvent.game_over(data_penalize, game_data)
            else:
                await move(data_penalize, game_data.get(GAME_NAME))


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
        next_turn(data.game_id)
        end_data = make_end_data_for_web(data.turn_data)
        data.turn_data["game_id"] = data.game_id
        await notify_end_game_to_client(game.get(PLAYERS), data.turn_data)
        await notify_end_game_to_web(data.game_id, game.get(TOURNAMENT_ID), end_data)
