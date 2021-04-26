import unittest
import server.server as server
from unittest.mock import MagicMock, patch, AsyncMock
import starlette
from parameterized import parameterized
from server.game import Game


class TestServer(unittest.IsolatedAsyncioTestCase):

    async def test_session_open_close(self):
        websocket = AsyncMock()
        websocket.receive_text.side_effect = starlette.websockets.WebSocketDisconnect()

        with patch('server.server.manager', new_callable=AsyncMock) as manager_patched:
            manager_patched.connect.return_value = 'User 1'
            manager_patched.remove_user = MagicMock()
            await server.session(websocket, 'token')
            manager_patched.connect.assert_called_with(websocket, 'token')
            manager_patched.remove_user.assert_called_with('User 1')

    async def test_session_invalid_client(self):
        websocket = MagicMock()
        websocket.close = AsyncMock()

        add_user_patched = MagicMock()
        add_user_patched.return_value = None
        server.add_user = add_user_patched

        await server.session(websocket, 'token')

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_accept_challenge(self, data):
        client = {'Test Client 1'}
        game = Game('player1', 'player2', 123213123)
        game.uuid_game = "c303282d-f2e6-46ca-a04a-35d3d873712d"
        server.games = [game]
        with patch('server.server.notify_game_created'):
            with patch('server.websockets.notify_error_to_client', new_callable=AsyncMock):
                await server.accept_challenge(data, client)
                self.assertEqual(game.state, 'accepted')
