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
            if game.uuid_game == game_id:
                await self.start_game(game)
                notify_game_created(game.challenge_id, game_id)

    async def start_game(self, game: Game):
        game.state = 'accepted'
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        await adapter.create_game(game.players)


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
            if game.uuid_game == game_id:
                data_received = await self.execute_action(game)
                client = data_received.get('data', {}).get('current_player')
                data_received.update({'id_game': game.uuid_game})
                return await notify_your_turn(
                    client,
                    data_received
                )

    async def execute_action(self, game: Game):
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        return await adapter.execute_action(game.uuid_game, self.response)
