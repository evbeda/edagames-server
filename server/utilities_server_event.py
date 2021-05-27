import asyncio

from server.game import next_turn, identifier, data_challenge
from server.redis_interface import redis_save, redis_get
from server.grpc_adapter import GRPCAdapterFactory
from server.exception import GameIdException
from server.websockets import (
    notify_challenge_to_client,
    notify_your_turn,
    notify_error_to_client,
    notify_end_game_to_client,
)
from server.web_requests import notify_end_game_to_web

from server.constants import (
    TIME_SLEEP,
    TURN_TOKEN,
    GAME_ID,
    DATA,
    PLAYERS,
    CHALLENGE_ID,
    TOKEN_COMPARE,
)


async def make_challenge(challenger, challenged, tournament_id, game_name):
    challenge_id = identifier()
    players = [challenger, *challenged]
    redis_save(
        challenge_id,
        data_challenge(players, tournament_id, game_name),
        CHALLENGE_ID,
    )
    await notify_challenge_to_client(
        challenged,
        challenger,
        challenge_id,
    )


async def make_move(data):
    turn_token = next_turn(data.game_id)
    data.turn_data.update({
        TURN_TOKEN: turn_token,
        GAME_ID: data.game_id,
    })
    await notify_your_turn(
        data.current_player,
        data.turn_data,
    )
    return turn_token


async def make_penalize(data, game_name, past_token):
    await asyncio.sleep(TIME_SLEEP)
    token_valid = await redis_get(
        data.game_id,
        TOKEN_COMPARE,
        data.current_player,
    )
    if token_valid == past_token:
        adapter = await GRPCAdapterFactory.get_adapter(game_name)
        data = await adapter.penalize(data.game_id)
        await make_move(data)


def make_end_data_for_web(data):
    return [
        (value, data.get('score_' + key[7]))
        for key, value in data.items() if 'player_' in key
    ]


class ServerEvent:
    def __init__(self, response, client):
        self.response = response
        self.client = client

    async def search_value(self, value):
        value_search = self.response.get(DATA, {}).get(value)
        if value_search is None:
            await notify_error_to_client(
                self.client,
                str(GameIdException),
            )
        return value_search

    async def move(self, data, game_name: str):
        token = await make_move(data)
        asyncio.create_task(make_penalize(data, game_name, token))

    async def game_over(self, data, game: dict):
        next_turn(data.game_id)
        end_data = make_end_data_for_web(data.turn_data)
        await notify_end_game_to_client(game.get(PLAYERS), data.turn_data)
        await notify_end_game_to_web(data.game_id, end_data)
