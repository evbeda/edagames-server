from server.connection_manager import manager
from server.game import games, Game
from server.websockets import (
    notify_user_list_to_client,
    notify_end_game_to_client,
)
from server.web_requests import (
    notify_end_game_to_web,
)
from server.grpc_adapter import GRPCAdapterFactory
from server.utilities_server_event import (
    MovesActions,
)

from server.constants import (
    GAME_STATE_ACCEPTED,
    GAME_STATE_ENDED,
    LAST_PLAYER,
    LIST_USERS,
    CHALLENGE_ACCEPTED,
    MOVEMENTS
)


class ServerEvent(object):
    def __init__(self, response, client):
        self.response = response
        self.client = client

    def run(self):
        raise NotImplementedError


class ListUsers(ServerEvent):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = LIST_USERS

    async def run(self):
        users = list(manager.connections.keys())
        await notify_user_list_to_client(self.client, users)


class AcceptChallenge(ServerEvent, MovesActions):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = CHALLENGE_ACCEPTED

    async def run(self):
        challenge_id = await self.search_value(self.response, self.client, 'challenge_id')
        for game in games:
            if game.challenge_id == challenge_id:
                await self.start_game(game)

    async def start_game(self, game: Game):
        game.state = GAME_STATE_ACCEPTED
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        data_received = await adapter.create_game(game.players)
        await self.make_move(game, data_received)


class Movements(ServerEvent, MovesActions):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = MOVEMENTS

    async def run(self):
        turn_token = await self.search_value(self.response, self.client, 'turn_token')
        for game in games:
            if game.turn_token == turn_token:
                game.timer.cancel()
                await self.execute_action(game)

    async def execute_action(self, game: Game):
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        data_received = await adapter.execute_action(
            game.game_id,
            self.response
        )
        if data_received.current_player == LAST_PLAYER:
            game.state = GAME_STATE_ENDED
            await notify_end_game_to_client(
                game.players,
                data_received.turn_data,
            )
            end_data = await self.end_data_for_web(data_received.turn_data)
            await notify_end_game_to_web(game.game_id, end_data)
        else:
            await self.make_move(game, data_received)

    async def end_data_for_web(self, data):
        return sorted([
            (value, data.get('score_' + key[7]))
            for key, value in data.items() if 'player' in key
        ])
