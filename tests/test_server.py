import unittest
from parameterized import parameterized
import server.server as server
from unittest.mock import MagicMock, patch, AsyncMock
import os
import json
import starlette
import server.websocket_events as websocket_events
import server.django_urls as django_urls
from server.connection_manager import ConnectionManager
from server.websockets import notify_challenge_to_client

os.environ['TOKEN_KEY'] = 'EDAGame$!2021'


class TestServer(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVGVzdCBDbGllbnQgMSJ9'
            '.zrXQiT77v9jnUVsZHr41HAZVDnJtRa84t8hmRVdzPck',
            'Test Client 1',
        )
    ])
    def test_add_user_ok(self, token, expected):
        client = server.add_user(token)
        self.assertEqual(client, expected)

    def test_remove_user(self):
        server.manager.connections = {'Test Client 1': 'websocket'}
        server.remove_user("Test Client 1")
        self.assertEqual({}, server.manager.connections)

    @parameterized.expand([
        (
            '/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiVXNlciBUZXN0NCJ9.'
            'p6MnNJLD5jwTH1C0PvqUb-spfc7XW7xf6gQjSiDrktg&action=NULL&msg=NULL',
            'Test Client 1',
        )
    ])
    def test_add_user_token_fail(self, token, expected):
        server.add_user(token)
        self.assertNotIn(expected, server.manager.connections)

    async def test_session_open_close(self):
        websocket = MagicMock()
        websocket.receive_text = AsyncMock()
        websocket.receive_text.side_effect = starlette.websockets.WebSocketDisconnect()

        add_user_patched = MagicMock()
        add_user_patched.return_value = 'User 1'
        server.add_user = add_user_patched

        manager_patched = MagicMock()
        manager_patched.connect = AsyncMock()
        server.manager = manager_patched

        server.remove_user = MagicMock()

        await server.session(websocket, 'token')
        server.manager.connect.assert_called_with(websocket, 'User 1')
        server.remove_user.assert_called_with('User 1')

    async def test_session_invalid_client(self):
        websocket = MagicMock()
        websocket.close = AsyncMock()

        add_user_patched = MagicMock()
        add_user_patched.return_value = None
        server.add_user = add_user_patched

        await server.session(websocket, 'token')

    @patch('requests.post')
    def test_update_users_in_django(self, post_patched):
        user_list = {"users": ["User 1"]}
        user_dict = {'User 1': 'websockets'}

        server.manager.connections = user_dict

        server.update_users_in_django()

        post_patched.assert_called_with(
            django_urls.USERS_URL,
            json=json.dumps(user_list)
        )

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
