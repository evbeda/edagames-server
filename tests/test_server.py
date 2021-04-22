import unittest
import server.server as server
from unittest.mock import MagicMock, patch, AsyncMock
import json
import starlette
import server.websocket_events as websocket_events
import server.django_urls as django_urls
from server.connection_manager import ConnectionManager
from server.websockets import notify_challenge_to_client
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

    @patch('requests.post')
    def test_notify_game_created(self, post_patched):
        server.notify_game_created(
            '00000000-0000-0000-0000-000000000001',
            '123e4567-e89b-12d3-a456-426614174000',
        )

        post_patched.assert_called_with(
            django_urls.GAME_URL,
            json=json.dumps({
                'challenge_id': '00000000-0000-0000-0000-000000000001',
                'game_id': '123e4567-e89b-12d3-a456-426614174000',
            })
        )

    @patch.object(ConnectionManager, 'send', new_callable=AsyncMock)
    async def test_notify_challenge_to_client(self, send_patched):
        challenge_sender = 'User 1'
        challenge_receiver = 'User 2'
        test_game_id = '00000000-0000-0000-0000-000000000001'
        await notify_challenge_to_client(
            challenge_receiver,
            challenge_sender,
            test_game_id,
        )
        send_patched.assert_called_with(
            challenge_receiver,
            websocket_events.EVENT_SEND_CHALLENGE,
            {
                'opponent': challenge_sender,
                'game_id': test_game_id,
            },
        )

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
