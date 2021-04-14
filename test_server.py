import unittest
from parameterized import parameterized
from server import session
import server
from unittest.mock import MagicMock
from server import add_user


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
            await session(websocket, path)
        self.assertNotIn(user_name, server.users_connected)

    def test_remove_user(self):
        server.users_connected = {"Usuario Test 1", "Usuario Test 2"}
        server.users_connected.remove("Usuario Test 1")
        self.assertEqual({"Usuario Test 2"}, server.users_connected)

    @parameterized.expand([
        ('/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVXNlciBUZXN0MSJ9.nsn153OEb8vMoieBF91b6h9zORlniwdbJ-RL1exsQs0&action=NULL&msg=NULL',
         'User Test1',)
    ])
    def test_add_user_ok(self, path, user):
        add_user(path)
        self.assertIn(user, server.users_connected)

    @parameterized.expand([
        ('/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVXNlciBUZXN0MSJ9.958U6hN_SUIaaGG4YT1f0aiyBODBXZIjGLOevZpY1qs&action=NULL&msg=NULL'),
    ])
    def test_add_user_fail(self, path):
        with self.assertRaises(Exception):
            add_user(path)
