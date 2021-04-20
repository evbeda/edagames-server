import unittest
from parameterized import parameterized
import server.server as server
from server.server import add_user, manager, remove_user
from unittest.mock import MagicMock, patch, AsyncMock
import os
import json

os.environ['TOKEN_KEY'] = 'EDAGame$!2021'


def true_once():
    yield True
    yield False


class MockTrueFunc(object):

    def __init__(self):
        self.gen = true_once()

    def __call__(self):
        return next(self.gen)


class TestServer(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVGVzdCBDbGllbnQgMSJ9'
            '.zrXQiT77v9jnUVsZHr41HAZVDnJtRa84t8hmRVdzPck',
            'Test Client 1',
        )
    ])
    def test_add_user_ok(self, token, expected):
        client = add_user(token)
        self.assertEquals(client, expected)

    def test_remove_user(self):
        manager.connections = {'Test Client 1': 'websocket'}
        remove_user("Test Client 1")
        self.assertEqual({}, manager.connections)

    @parameterized.expand([
        (
            '/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiVXNlciBUZXN0NCJ9.'
            'p6MnNJLD5jwTH1C0PvqUb-spfc7XW7xf6gQjSiDrktg&action=NULL&msg=NULL',
            'Test Client 1',
        )
    ])
    def test_add_user_token_fail(self, token, expected):
        add_user(token)
        self.assertNotIn(expected, manager.connections)

    @parameterized.expand([
        (
            'Test Client 1',
        )
    ])
    async def test_connect(self, client):
        websocket = MagicMock()
        websocket.accept = AsyncMock()

        await server.ConnectionManager.connect(websocket, client)
        websocket.accept().assert_called()

    # @parameterized.expand([
    #     (
    #         'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVGVzdCBDbGllbnQgMSJ9'
    #         '.zrXQiT77v9jnUVsZHr41HAZVDnJtRa84t8hmRVdzPck',
    #     )
    # ])
    # @patch("server.server.add_user", return_value="User 1")
    # @patch("server.server.true_func", new_callable=MockTrueFunc)
    # async def test_session_methods(self, mock_true, mock_path, token):
    #     websocket = MagicMock()
    #     websocket.close = AsyncMock()
    #     websocket.accept = AsyncMock()

    #     await server.session(websocket, token)
    #     websocket.accept.assert_called()

    @patch('requests.post')
    def test_update_users_in_django(self, post_patched):
        user_list = set(['User 1', 'User 2'])
        user_dict = {'users': list(user_list)}

        server.manager.connections = user_list

        server.update_users_in_django()

        post_patched.assert_called_with(
            server.DJANGO_USERS_URI,
            json=json.dumps(user_dict)
        )

    @patch('requests.post')
    def test_notify_game_created(self, post_patched):
        server.notify_game_created(
            '00000000-0000-0000-0000-000000000001',
            '123e4567-e89b-12d3-a456-426614174000',
        )

        post_patched.assert_called_with(
            server.DJANGO_GAME_URI,
            json=json.dumps({
                'challenge_id': '00000000-0000-0000-0000-000000000001',
                'game_id': '123e4567-e89b-12d3-a456-426614174000',
            })
        )
