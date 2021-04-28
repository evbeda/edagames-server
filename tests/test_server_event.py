import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from parameterized import parameterized

from server.game import Game, games

from server.server_event import (
    AcceptChallenge,
    Movements,
    ListUsers,
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
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as g_adapter_patched:
            with patch('server.server_event.notify_your_turn') as notify_patched:
                adapter_patched = AsyncMock()
                adapter_patched.create_game.return_value = MagicMock()
                g_adapter_patched.return_value = adapter_patched
                await AcceptChallenge({}, 'client').start_game(self.game)
                self.assertEqual(self.game.state, 'accepted')
                g_adapter_patched.assert_called_with(self.game.name)
                notify_patched.assert_called()

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"turn_token": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_Movements(self, data):
        client = 'Test Client 1'
        with patch('server.server_event.notify_error_to_client', new_callable=AsyncMock):
            with patch('server.server_event.notify_your_turn', new_callable=AsyncMock):
                game = Game('player1', 'player2', 123213123)
                game.turn_token = 'c303282d-f2e6-46ca-a04a-35d3d873712d'
                games.append(game)
                with patch.object(Movements, 'execute_action') as start_patched:
                    await Movements(data, client).run()
                    start_patched.assert_called()

    async def test_list_users(self):
        data = {'action': 'list_users'}
        client = 'User 1'
        users = ['User 1', 'User 2', 'User 3']

        with patch('server.server_event.notify_user_list_to_client', new_callable=AsyncMock) as notify_patched,\
                patch('server.server_event.manager') as manager_patched:
            manager_patched.connections.keys.return_value = users
            await ListUsers(data, client).run()
            notify_patched.assert_called_with(client, users)

    async def test_execute_action(self):
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as Gadapter_patched:
            with patch('server.server_event.notify_your_turn') as notify_patched:
                adapter_patched = AsyncMock()
                adapter_patched.execute_action.return_value = MagicMock()
                Gadapter_patched.return_value = adapter_patched
                await Movements({}, 'client').execute_action(self.game)
                Gadapter_patched.assert_called_with(self.game.name)
                notify_patched.assert_called()
