from edagames_grpc.client import ClientGRPC

# from server.environment import FAKE_SERVICE_DISCOVERY_GAME_HOST_PORT
from server.environment import (
    GAME_HOST,
    GAME_PORT,
)


cached_adapters = {}


def discover_game(game_name: str):
    return FAKE_SERVICE_DISCOVERY_GAME_HOST_PORT.split(':')


class GRPCAdapterFactory:
    @staticmethod
    async def get_adapter(game_name: str):
        try:
            adapter = cached_adapters[game_name]
        except KeyError:
            # Service discovery goes here (?
            # adapter = ClientGRPC(*discover_game(game_name))
            adapter = ClientGRPC(GAME_HOST, GAME_PORT)
            cached_adapters[game_name] = adapter
        return adapter
