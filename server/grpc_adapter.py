# from eda5grpc.client import Client

from server.environment import FAKE_SERVICE_DISCOVERY_QUORIDOR_HOST_PORT


cached_adapters = {}


class Client:
    def __init__(self, *args):
        pass

    async def create_game(self, players):
        return 'test-00000001'

    async def execute_action(self, id, data_dict):
        return {'idgame': '123e4567-e89b-12d3-a456-426614174000', 'data': {}}


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
