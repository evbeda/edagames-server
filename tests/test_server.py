import unittest
import server.server as server
from unittest.mock import patch
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
