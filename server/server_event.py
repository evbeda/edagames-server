from server.connection_manager import manager
from server.game import games, Game
from server.websockets import (
    notify_error_to_client,
    notify_your_turn,
    notify_user_list_to_client,
    notify_end_game_to_client,
)
from server.web_requests import (
    notify_end_game_to_web,
)
from server.exception import GameIdException
from server.grpc_adapter import GRPCAdapterFactory
from server.constants import (
    GAME_STATE_ACCEPTED,
    GAME_STATE_ENDED,
    LAST_PLAYER,
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
        self.nameEvent = 'List users'

    async def run(self):
        users = list(manager.connections.keys())
        await notify_user_list_to_client(self.client, users)


class AcceptChallenge(ServerEvent):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.nameEvent = 'Challenge accepted'

    async def run(self):
        challenge_id = self.response.get('data', {}).get('game_id')
        if challenge_id is None:
            return await notify_error_to_client(
                self.client,
                str(GameIdException),
            )
        for game in games:
            if game.challenge_id == challenge_id:
                await self.start_game(game)

    async def start_game(self, game: Game):
        game.state = GAME_STATE_ACCEPTED
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        game_start_state = await adapter.create_game(game.players)
        game.next_turn()
        game.game_id = game_start_state.game_id
        game_start_state.turn_data.update({'turn_token': game.turn_token})
        await notify_your_turn(
            game_start_state.current_player,
            game_start_state.turn_data,
        )


class Movements(ServerEvent):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.nameEvent = 'movements'

    async def run(self):
        turn_token = self.response.get('data', {}).get('turn_token')
        if turn_token is None:
            return await notify_error_to_client(
                self.client,
                str(GameIdException),
            )
        for game in games:
            if game.turn_token == turn_token:
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
            end_data = self.end_data(data_received.turn_data)
            notify_end_game_to_web(game.game_id, end_data)
        else:
            game.next_turn()
            data_received.turn_data.update({'turn_token': game.turn_token})
            await notify_your_turn(
                data_received.current_player,
                data_received.turn_data,
            )

    def end_data(self, data):
        return 'nada'
