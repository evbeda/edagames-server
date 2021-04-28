from server.game import games, Game
from server.websockets import (
    notify_error_to_client,
    notify_your_turn
)
from server.web_requests import notify_game_created
from server.exception import GameIdException
from server.grpc_adapter import GRPCAdapterFactory


class ServerEvent(object):
    def run(self):
        raise NotImplementedError


class AcceptChallenge(ServerEvent):
    def __init__(self, response, client):
        self.response = response
        self.client = client
        self.nameEvent = 'Challenge accepted'

    async def run(self):
        game_id = self.response.get('data', {}).get('game_id')
        if game_id is None:
            return await notify_error_to_client(
                self.client,
                str(GameIdException),
            )
        for game in games:
            if game.game_id == game_id:
                await self.start_game(game)
                notify_game_created(game.challenge_id, game_id)

    async def start_game(self, game: Game):
        game.state = 'accepted'
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        game_start_state = await adapter.create_game(game.players)
        game.next_turn()
        await notify_your_turn(
            game_start_state.current_player,
            game_start_state.turn_data.update({'turn_token': game.turn_token}),
        )


class Movements(ServerEvent):
    def __init__(self, response, client):
        self.response = response
        self.client = client
        self.nameEvent = 'movements'

    async def run(self):
        game_id = self.response.get('data', {}).get('game_id')
        if game_id is None:
            return await notify_error_to_client(
                self.client,
                str(GameIdException),
            )
        for game in games:
            if game.game_id == game_id:
                await self.execute_action(game)

    async def execute_action(self, game: Game):
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        data_received = await adapter.execute_action(game.game_id, self.response)
        game.next_turn()
        return await notify_your_turn(
            data_received.current_player,
            data_received.turn_data.update({'turn_token': game.turn_token}),
        )
