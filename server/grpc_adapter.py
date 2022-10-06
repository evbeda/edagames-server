from sqlite3 import adapters
from edagames_grpc.client import ClientGRPC

from server.environment import load_env_var

from server.constants import GAME_HOST_PORT



cached_adapters = {}


def discover_game(game_name: str):
    host_port = GAME_HOST_PORT[game_name]
    return load_env_var(host_port).split(':')

    # return FAKE_SERVICE_DISCOVERY_GAME_HOST_PORT.split(':')

# def discover(game_name: str):
#     return game_name.split(':')


class GRPCAdapterFactory:

    @staticmethod
    async def get_adapter(game_name: str):

        try:
            adapter = cached_adapters[game_name]
        except KeyError:
            # pass
            # Service discovery goes here (?
            adapter = ClientGRPC(*discover_game(game_name))
            cached_adapters[game_name] = adapter
        return adapter
