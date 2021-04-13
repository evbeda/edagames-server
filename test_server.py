import unittest
from parameterized import parameterized
from server import session
import server
from unittest.mock import MagicMock


class TestServer(unittest.IsolatedAsyncioTestCase):

    @parameterized.expand([
        ('/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlVzdWFyaW8gVGVzdDEifQ.dP91nnEzz1ZNrpSBgbPpxAYE-bnPdjrWTlx0dcMFXKw&action=NULL&msg=NULL',
         'EDAGame$!2021',
         'Usuario Test1',
         True),
    ])
    async def test_session_ok(self, path, token_key, user_name, expected):
        websocket = MagicMock
        await session(websocket, path, token_key)
        self.assertIn(user_name, server.users_connected)

    @parameterized.expand([
        ('/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlVzdWFyaW8gVGVzdDEifQ.MqozKCOnkwvV4mTgQcsO5FUDgVNi25t5dIKiZ6sOPu0&action=NULL&msg=NULL',
         'EDAGame$!2021',
         'Usuario Test1',
         False),
    ])
    async def test_session_fail(self, path, token_key, user_name, expected):
        websocket = MagicMock
        with self.assertRaises(Exception):
            await session(websocket, path, token_key)
        self.assertNotIn(user_name, server.users_connected)
