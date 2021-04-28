import unittest
from unittest.mock import patch, AsyncMock
from parameterized import parameterized

from server.game import Game, games
from server.grpc_adapter import GRPCAdapterFactory

from server.server_event import (
    AcceptChallenge,
    Movements,
)


class TestServerEvent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = Game('player1', 'player2', 123213123)

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_accept_challenge(self, data):
        client = 'Test Client 1'
        with patch('server.server_event.notify_game_created'):
            with patch('server.server_event.notify_error_to_client', new_callable=AsyncMock):
                with patch('uuid.uuid4', return_value='c303282d-f2e6-46ca-a04a-35d3d873712d'):
                    game = Game('player1', 'player2', 123213123)
                    games.append(game)
                    with patch.object(AcceptChallenge, 'start_game') as start_patched:
                        await AcceptChallenge(data, client).run()
                        start_patched.assert_called()

    async def test_start_game(self):
        with patch.object(GRPCAdapterFactory, 'get_adapter', new_callable=AsyncMock) as get_adapter_patched:
            await AcceptChallenge({}, 'client').start_game(self.game)
            self.assertEqual(self.game.state, 'accepted')
            get_adapter_patched.assert_called_with(self.game.name)

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_Movements(self, data):
        client = 'Test Client 1'
        with patch('server.server_event.notify_error_to_client', new_callable=AsyncMock):
            with patch('server.server_event.notify_your_turn', new_callable=AsyncMock):
                with patch('uuid.uuid4', return_value='c303282d-f2e6-46ca-a04a-35d3d873712d'):
                    game = Game('player1', 'player2', 123213123)
                    games.append(game)
                    with patch.object(Movements, 'execute_action', return_value={}) as start_patched:
                        await Movements(data, client).run()
                        start_patched.assert_called()

    async def test_execute_action(self):
        with patch.object(GRPCAdapterFactory, 'get_adapter', new_callable=AsyncMock) as get_adapter_patched:
            await Movements({}, 'client').execute_action(self.game)
            get_adapter_patched.assert_called_with(self.game.name)
