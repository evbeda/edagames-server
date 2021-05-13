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
    PREFIX_TURN_TOKEN,
)


async def move(game_id, data):
    turn_token = next_turn(game_id)
    data.turn_data.update({
        'turn_token': turn_token,
        'board_id': game_id,
    })
    await notify_your_turn(
        data.current_player,
        data.turn_data,
    )


async def penalize(game_id, game_name):
    await asyncio.sleep(TIME_SLEEP)
    token_valid = await get_string(f'{PREFIX_TURN_TOKEN}{game_id}')
    if token_valid is None:
        adapter = await GRPCAdapterFactory.get_adapter(game_name)
        data = await adapter.penalize(game_id)
        await move(game_id, data)


def end_data_for_web(data):
    return sorted([
        (value, data.get('score_' + key[7]))
        for key, value in data.items() if 'player' in key
    ])


class MovesActions:
    async def make_move(self, game_name: str, data):
        await move(data)
        asyncio.create_task(penalize(data.game_id, game_name))

    async def search_value(self, response, client, value):
        value_search = response.get('data', {}).get(value)
        if value_search is None:
            await notify_error_to_client(
                client,
                str(GameIdException),
            )
        return value_search


class EndActions:
    async def game_over(self, game: dict, data):
        await notify_end_game_to_client(
            game.get('players'),
            data.turn_data,
        )
        end_data = end_data_for_web(data.turn_data)
        await notify_end_game_to_web(game.get('game_id'), end_data)
