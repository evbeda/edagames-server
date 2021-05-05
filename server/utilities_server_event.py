import asyncio

from server.game import Game
from server.constants import TIME_SLEEP
from server.grpc_adapter import GRPCAdapterFactory
from server.exception import GameIdException
from server.websockets import (
    notify_your_turn,
    notify_error_to_client
)


async def penalize(game: Game):
    await asyncio.sleep(TIME_SLEEP)
    adapter = await GRPCAdapterFactory.get_adapter(game.name)
    game_start_state = await adapter.penalize(game.game_id)
    game.next_turn()
    game_start_state.turn_data.update({'turn_token': game.turn_token})
    await notify_your_turn(
        game_start_state.current_player,
        game_start_state.turn_data,
    )


async def search_value(response, client, value):
    value_search = response.get('data', {}).get(value)
    if value_search is None:
        return await notify_error_to_client(
            client,
            str(GameIdException),
        )
    return value_search


class MovesActions:
    async def make_move(self, game, data):
        game.next_turn()
        data.turn_data.update({'turn_token': game.turn_token})
        await notify_your_turn(
            data.current_player,
            data.turn_data,
        )
        game.timer = asyncio.create_task(penalize(game))
