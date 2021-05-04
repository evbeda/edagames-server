from server.game import Game
from server.constants import TIME_SLEEP
import asyncio
from server.grpc_adapter import GRPCAdapterFactory
from server.websockets import notify_your_turn


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
