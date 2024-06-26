from server.websockets import notify_feedback, notify_user_list_to_client
# from server.grpc_adapter import GRPCAdapterFactory
from server.utilities_server_event import ServerEvent, make_challenge, start_game, move
from server.redis_interface import (
    log_action,
    redis_save,
    redis_get,
)
from server.constants import (
    ABORT_GAME,
    ACCEPT_CHALLENGE,
    ASK_CHALLENGE,
    CHALLENGE_ID,
    CLIENT_LIST,
    CLIENT_LIST_KEY,
    CURRENT_PLAYER,
    DEBUG_MODE,
    DEFAULT_GAME,
    EMPTY_PLAYER,  # game_over
    GAME_ID,
    GAME_NAME,  # dict.get values
    LIST_USERS,  # name_event
    MOVEMENTS,
    MSG_TURN_TOKEN,
    OPPONENT,
    TURN_TOKEN,
)
from server.web_requests import (
    execute_action_to_game,
)


class ListUsers(ServerEvent):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = LIST_USERS

    async def run(self):
        users = await redis_get(CLIENT_LIST_KEY, CLIENT_LIST)
        await notify_user_list_to_client(self.client, users)


class Challenge(ServerEvent):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = ASK_CHALLENGE

    async def run(self):
        challenged = await self.search_value(OPPONENT)
        game_name = await self.search_value(GAME_NAME, DEFAULT_GAME)
        await make_challenge(self.client, challenged, game_name)


class AcceptChallenge(ServerEvent):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = ACCEPT_CHALLENGE

    async def run(self):
        challenge_id = await self.search_value(CHALLENGE_ID)
        if challenge_id is not None:
            game_data = await redis_get(
                challenge_id,
                CHALLENGE_ID,
                self.client,
            )
            if game_data is not None:
                if self.client not in game_data['accepted']:
                    game_data['accepted'].append(self.client)
                if self.client in game_data['players']:
                    if all([player in game_data['accepted'] for player in game_data['players']]):
                        await start_game(game_data)
                    else:
                        await redis_save(
                            challenge_id,
                            game_data,
                            CHALLENGE_ID,
                        )


class Movements(ServerEvent):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = MOVEMENTS

    async def run(self):
        turn_token = await self.search_value(TURN_TOKEN)
        game_id = await self.search_value(GAME_ID)
        redis_game_id = await redis_get(
            game_id,
            TURN_TOKEN,
            self.client,
        )
        if redis_game_id is None:
            await notify_feedback(
                self.client,
                f'{MSG_TURN_TOKEN}{game_id}',
            )
        elif redis_game_id == turn_token:
            game = await redis_get(
                game_id,
                GAME_ID,
                self.client,
            )
            if game is not None:
                await self.execute_action(game, game_id)

    async def execute_action(self, game_data: dict, game_id: str):
        # adapter = await GRPCAdapterFactory.get_adapter(game_data.get(GAME_NAME))
        # data_received = await adapter.execute_action(
        #     game_id,
        #     self.response
        # )
        await log_action(game_id, self.response)
        data_received = await execute_action_to_game(game_id, self.response)
        await log_action(game_id, data_received)
        # TODO: END CONDITION?
        if data_received[CURRENT_PLAYER] == EMPTY_PLAYER:
            await self.game_over(data_received, game_data)
        else:
            await move(
                data_received,
                game_data.get(GAME_NAME),
                game_data.get(DEBUG_MODE),
            )


class AbortGame(ServerEvent):
    def __init__(self, response, client):
        super().__init__(response, client)
        self.name_event = ABORT_GAME

    async def run(self):
        turn_token_received = await self.search_value(TURN_TOKEN)
        game_id = await self.search_value(GAME_ID)
        turn_token_saved = await redis_get(
            game_id,
            TURN_TOKEN,
            self.client,
        )
        if turn_token_received == turn_token_saved:
            game = await redis_get(
                game_id,
                GAME_ID,
                self.client,
            )
            if game is not None:
                await self.end_game(game, game_id)

    async def end_game(self, game: dict, game_id: str):
        # adapter = await GRPCAdapterFactory.get_adapter(game.get(GAME_NAME))
        # data_received = await adapter.end_game(game_id)
        data_received = await abort_to_game(game_id)
        await self.game_over(data_received, game)
