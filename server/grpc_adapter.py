# from edagames_grpc.client import Client

from server.environment import FAKE_SERVICE_DISCOVERY_QUORIDOR_HOST_PORT


cached_adapters = {}


class Client:
    def __init__(self, *args):
        pass

    async def create_game(self, players):
        return 'test-00000001'


def discover_game(game_name: str):
    return FAKE_SERVICE_DISCOVERY_QUORIDOR_HOST_PORT


class GRPCAdapterFactory:
    @staticmethod
    async def get_adapter(game_name: str):
        try:
            adapter = cached_adapters[game_name]
        except KeyError:
            # Service discovery goes here (?
            adapter = Client(discover_game(game_name))
            cached_adapters[game_name] = adapter
        return adapter
