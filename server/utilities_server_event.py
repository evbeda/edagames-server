import asyncio

from server.game import next_turn
from server.redis import get_string
from server.grpc_adapter import GRPCAdapterFactory
from server.exception import GameIdException
from server.websockets import (
    notify_your_turn,
    notify_error_to_client,
    notify_end_game_to_client,
)
from server.web_requests import notify_end_game_to_web

from server.constants import (
    TIME_SLEEP,
    TURN_TOKEN,
    PREFIX_TURN_TOKEN,
)


async def move(data):
    turn_token = next_turn(data.game_id)
    data.turn_data.update({
        'turn_token': turn_token,
        'board_id': data.game_id,
    })
    await notify_your_turn(
        data.current_player,
        data.turn_data,
    )
    return turn_token


async def penalize(data, game_name, past_token):
    await asyncio.sleep(TIME_SLEEP)
    token_valid = await get_string(
        f'{PREFIX_TURN_TOKEN}{data.game_id}',
        data.current_player,
        TURN_TOKEN,
    )
    if token_valid == past_token:
        adapter = await GRPCAdapterFactory.get_adapter(game_name)
        data = await adapter.penalize(data.game_id)
        await move(data)


def end_data_for_web(data):
    return sorted([
        (value, data.get('score_' + key[7]))
        for key, value in data.items() if 'player' in key
    ])


class ServerEvent:
    def __init__(self, response, client):
        self.response = response
        self.client = client

    async def search_value(self, value):
        value_search = self.response.get('data', {}).get(value)
        if value_search is None:
            await notify_error_to_client(
                self.client,
                str(GameIdException),
            )
        return value_search

    async def make_move(self, data, game_name: str):
        token = await move(data)
        asyncio.create_task(penalize(data, game_name, token))

    async def game_over(self, data, game: dict):
        await notify_end_game_to_client(
            game.get('players'),
            data.turn_data,
        )
        next_turn(data.game_id)
        end_data = end_data_for_web(data.turn_data)
        await notify_end_game_to_web(data.game_id, end_data)
