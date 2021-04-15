import unittest
from parameterized import parameterized
from server import session
import server
from unittest.mock import MagicMock
from server import add_user


class TestServer(unittest.IsolatedAsyncioTestCase):

    @parameterized.expand([
        ('/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVXNlciBUZXN0NCJ9.p6MnNJLD5jwTH1C0PvqUb-spfc7XW7xf6gQjSiDrktg&action=NULL&msg=NULL',
         'User Test4',)
    ])
    def test_add_user_token_fail(self, path, user):
        add_user(path)
        str_us_con = str(server.users_connected)
        self.assertNotIn(str_us_con, user)

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
        ('/'),
    ])
    def test_add_user_path_fail(self, path):
        with self.assertRaises(Exception):
            add_user(path)
