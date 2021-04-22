import unittest
from parameterized import parameterized
from unittest.mock import MagicMock, AsyncMock
from server.connection_manager import ConnectionManager
import json


class TestConnectionManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.manager = ConnectionManager()

    @parameterized.expand([
        (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVGVzdCBDbGllbnQgMSJ9'
            '.zrXQiT77v9jnUVsZHr41HAZVDnJtRa84t8hmRVdzPck',
            'Test Client 1',
        )
    ])
    async def test_connect_valid(self, token, expected):
        websocket = AsyncMock()
        client = await self.manager.connect(websocket, token)
        self.assertEqual(client, expected)
        websocket.accept.assert_called()

    @parameterized.expand([
        (
            '/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiVXNlciBUZXN0NCJ9.'
            'p6MnNJLD5jwTH1C0PvqUb-spfc7XW7xf6gQjSiDrktg&action=NULL&msg=NULL',
            'Test Client 1',
        )
    ])
    async def test_connect_invalid(self, token, expected):
        websocket = AsyncMock()
        await self.manager.connect(websocket, token)
        self.assertNotIn(expected, self.manager.connections)
        websocket.close.assert_called()

    def test_remove_user(self):
        self.manager.connections = {'Test Client 1': 'websocket'}
        self.manager.remove_user('Test Client 1')
        self.assertEqual({}, self.manager.connections)

    @parameterized.expand([
        (
            'Test Message 1',
        )
    ])
    async def test_broadcast(self, data):
        connection = MagicMock()
        connection.send_text = AsyncMock()
        self.manager.connections = {'Test Client 1': connection}

        await self.manager.broadcast(data)
        connection.send_text.assert_called()

    async def test_manager_send(self):
        user = 'User'
        event = 'event'
        data = {
            'data': 'some data',
            'other_data': 'some other data',
        }

        websocket_patched = MagicMock()
        websocket_patched.send_text = AsyncMock()
        self.manager.connections = {
            user: websocket_patched,
        }

        await self.manager.send(
            user,
            event,
            data,
        )

        websocket_patched.send_text.assert_called_with(
            json.dumps({
                'event': event,
                'data': data
            })
        )
