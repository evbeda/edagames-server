import asyncio

from server.game import Game
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
    GAME_STATE_ENDED,
)


async def move(game, data):
    game.next_turn()
    data.turn_data.update({
            'turn_token': game.turn_token,
            'board_id': game.game_id,
    })
    await notify_your_turn(
        data.current_player,
        data.turn_data,
    )


async def penalize(game: Game):
    await asyncio.sleep(TIME_SLEEP)
    adapter = await GRPCAdapterFactory.get_adapter(game.name)
    data = await adapter.penalize(game.game_id)
    # move(game, data)
    game.next_turn()
    data.turn_data.update({'turn_token': game.turn_token, 'board_id': game.game_id})
    await notify_your_turn(
        data.current_player,
        data.turn_data,
    )


async def end_data_for_web(data):
    return sorted([
        (value, data.get('score_' + key[7]))
        for key, value in data.items() if 'player' in key
    ])


class MovesActions:
    async def make_move(self, game, data):
        # move(game, data)
        game.next_turn()
        data.turn_data.update({'turn_token': game.turn_token, 'board_id': game.game_id})
        await notify_your_turn(
            data.current_player,
            data.turn_data,
        )
        game.timer = asyncio.create_task(penalize(game))

    async def search_value(self, response, client, value):
        value_search = response.get('data', {}).get(value)
        if value_search is None:
            await notify_error_to_client(
                client,
                str(GameIdException),
            )
        return value_search


class EndActions:
    async def game_over(self, game, data):
        game.state = GAME_STATE_ENDED
        await notify_end_game_to_client(
            game.players,
            data.turn_data,
        )
        end_data = await end_data_for_web(data.turn_data)
        await notify_end_game_to_web(game.game_id, end_data)
