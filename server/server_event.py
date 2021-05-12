from server.connection_manager import manager
from server.game import (
    games,
    Game,
    identifier,
    data_challenge,
)
from server.websockets import (
    notify_user_list_to_client,
    notify_challenge_to_client,
)
from server.grpc_adapter import GRPCAdapterFactory
from server.utilities_server_event import (
    MovesActions,
    EndActions,
)
from server.redis import save_string

from server.constants import (
    GAME_STATE_ACCEPTED,
    LAST_PLAYER,
    LIST_USERS,
    CHALLENGE_ACCEPTED,
    MOVEMENTS,
    OPPONENT,
    ASK_CHALLENGE,
    ABORT_GAME,
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
        challenge_id = await self.search_value(
            self.response,
            self.client,
            'challenge_id',
        )
        for game in games:
            if game.challenge_id == challenge_id:
                await self.start_game(game)

    async def start_game(self, game: Game):
        game.state = GAME_STATE_ACCEPTED
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        data_received = await adapter.create_game(game.players)
        game.game_id = data_received.game_id
        await self.make_move(game, data_received)


class Movements(ServerEvent, MovesActions, EndActions):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = MOVEMENTS

    async def run(self):
        turn_token = await self.search_value(
            self.response,
            self.client,
            'turn_token',
        )
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
            await self.game_over(game, data_received)
        else:
            await self.make_move(game, data_received)


class Challenge(ServerEvent, MovesActions):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = ASK_CHALLENGE

    async def run(self):
        challenged = await self.search_value(
            self.response,
            self.client,
            OPPONENT,
        )
        game = Game([self.client, challenged])
        games.append(game)
        challenge_id = identifier()
        save_string(
            challenge_id,
            data_challenge([self.client, challenged]),
        )
        await notify_challenge_to_client(
            challenged,
            self.client,
            challenge_id,
        )


class AbortGame(ServerEvent, MovesActions, EndActions):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = ABORT_GAME

    async def run(self):
        turn_token = await self.search_value(self.response, self.client, 'turn_token')
        for game in games:
            if game.turn_token == turn_token:
                game.timer.cancel()
                await self.end_game(game)

    async def end_game(self, game: Game):
        adapter = await GRPCAdapterFactory.get_adapter(game.name)
        data_received = await adapter.end_game(
            game.game_id
        )
        await self.game_over(game, data_received)
