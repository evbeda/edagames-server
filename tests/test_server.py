import unittest
from parameterized import parameterized
import server.server as server
from server.server import add_user
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
            '/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiVXNlciBUZXN0NCJ9.'
            'p6MnNJLD5jwTH1C0PvqUb-spfc7XW7xf6gQjSiDrktg&action=NULL&msg=NULL',
            'User Test4',
        )
    ])
    def test_add_user_token_fail(self, path, user):
        add_user(path)
        str_us_con = str(server.users_connected)
        self.assertNotIn(str_us_con, user)

    @parameterized.expand([
        (
            '/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiVXNlciBUZXN0MSJ9.'
            'nsn153OEb8vMoieBF91b6h9zORlniwdbJ-RL1exsQs0&action=NULL&msg=NULL',
            'User Test1',
        )
    ])
    def test_add_user_ok(self, path, user):

        add_user(path)
        self.assertIn(user, server.users_connected)

    @parameterized.expand([
        ('/'),
    ])
    def test_add_user_path_fail(self, path):
        with self.assertRaises(Exception):
            add_user(path)

    def test_remove_user(self):
        server.users_connected = {"Usuario Test 1", "Usuario Test 2"}
        server.users_connected.remove("Usuario Test 1")
        self.assertEqual({"Usuario Test 2"}, server.users_connected)

    @patch("server.server.add_user", return_value="User 1")
    @patch("server.server.true_func", new_callable=MockTrueFunc)
    async def test_session_methods(self, mock_true, mock_path):
        websocket = MagicMock()
        websocket.accept = AsyncMock()
        websocket.receive_text = AsyncMock()
        websocket.send_text = AsyncMock()

        await server.session(websocket)
        websocket.accept.assert_called()
        websocket.send_text.assert_called()

    @patch('requests.post')
    def test_update_users_in_django(self, post_patched):
        user_list = set(['User 1', 'User 2'])
        user_dict = {'users': list(user_list)}

        server.users_connected = user_list

        server.update_users_in_django()

        post_patched.assert_called_with(
            server.DJANGO_USERS_URI,
            json=json.dumps(user_dict)
        )
