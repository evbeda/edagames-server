import json
from typing import Dict

from server.connection_manager import manager
from server.game import (
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
from server.redis import save_string, get_string

from server.constants import (
    LAST_PLAYER,
    LIST_USERS,
    CHALLENGE_ACCEPTED,
    MOVEMENTS,
    OPPONENT,
    ASK_CHALLENGE,
    ABORT_GAME,
    CHALLENGE_ID,
    BOARD_ID,
    TURN_TOKEN,
    PREFIX_CHALLENGE,
    PREFIX_GAME,
    PREFIX_LOG,
    PREFIX_TURN_TOKEN,
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
            CHALLENGE_ID,
        )
        if challenge_id is not None:
            game_data = await get_string(
                f'{PREFIX_CHALLENGE}{challenge_id}',
                self.client,
                CHALLENGE_ID,
            )
            if game_data is not None:
                await self.start_game(json.loads(game_data))

    async def start_game(self, game_data: Dict):
        adapter = await GRPCAdapterFactory.get_adapter(game_data.get('name'))
        data_received = await adapter.create_game(game_data.get('players'))
        save_string(
            f'{PREFIX_GAME}{data_received.game_id}',
            game_data,
        )
        await self.make_move(data_received, game_data.get('name'))


class Movements(ServerEvent, MovesActions, EndActions):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = MOVEMENTS

    async def run(self):
        turn_token = await self.search_value(
            self.response,
            self.client,
            TURN_TOKEN,
        )
        game_id = await self.search_value(
            self.response,
            self.client,
            BOARD_ID,
        )
        redis_game_id = await get_string(
            f'{PREFIX_TURN_TOKEN}{game_id}',
            self.client,
        )
        if redis_game_id == turn_token:
            game = await get_string(
                f'{PREFIX_GAME}{game_id}',
                self.client,
            )
            if game is not None:
                await self.execute_action(json.loads(game), game_id)

    async def execute_action(self, game_data: dict, game_id: str):
        adapter = await GRPCAdapterFactory.get_adapter(game_data.get('name'))
        data_received = await adapter.execute_action(
            game_id,
            self.response
        )
        await self.log_action(data_received)
        if data_received.current_player == LAST_PLAYER:
            await self.game_over(game_data, data_received)
        else:
            await self.make_move(data_received, game_data.get('name'))

    async def log_action(self, data):
        save_string(
            f'{PREFIX_LOG}{data.game_id}',
            json.dumps({
                "turn": data.previous_player,
                "data": data.play_data,
            })
        )


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
        challenge_id = identifier()
        save_string(
            f'{PREFIX_CHALLENGE}{challenge_id}',
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
        turn_token_received = await self.search_value(
            self.response,
            self.client,
            TURN_TOKEN,
        )
        game_id = await self.search_value(
            self.response,
            self.client,
            BOARD_ID,
        )
        turn_token_saved = await get_string(
            f'{PREFIX_TURN_TOKEN}{game_id}',
            self.client,
        )
        if turn_token_received == turn_token_saved:
            game = await get_string(
                f'{PREFIX_LOG}{game_id}',
                self.client,
            )
            if game is not None:
                await self.end_game(json.loads(game), game_id)

    async def end_game(self, game: dict, game_id: str):
        adapter = await GRPCAdapterFactory.get_adapter(game.get('name'))
        data_received = await adapter.end_game(game_id)
        await self.game_over(game, data_received)
