import unittest
import json
from parameterized import parameterized
from unittest.mock import MagicMock, AsyncMock, patch

from server.connection_manager import ConnectionManager
import server.constants as websocket_events


class TestConnectionManager(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.manager = ConnectionManager()

    @parameterized.expand([
        (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVGVzdCBDbGllbnQgMSJ9'
            '.zrXQiT77v9jnUVsZHr41HAZVDnJtRa84t8hmRVdzPck',
            'Test Client 1',
        ),
        (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiUGVkcm8ifQ.'
            'h85yCXGm1BdXbKKnLgOJ52vHAdGmcUpJ5gfCgjYyAJQ',
            'Pedro',
        ),
        (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiUGFibG8ifQ.'
            '3qIB7M-S34ALo1XQQ-7V4Zvzou3SPL5lJsWbINHOFBc',
            'Pablo',
        ),
    ])
    async def test_connect_valid(self, token, expected):
        websocket = AsyncMock()
        notify_patched = AsyncMock()
        self.manager.notify_user_list_changed = notify_patched
        with patch('server.connection_manager.JWT_TOKEN_KEY', 'EDAGame$!2021'):
            client = await self.manager.connect(websocket, token)
        self.assertEqual(client, expected)
        websocket.accept.assert_called()
        notify_patched.assert_called()

    @parameterized.expand([
        (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiVXNlciBUZXN0NCJ9.'
            'p6MnNJLD5jwTH1C0PvqUb-spfc7XW7xf6gQjSiDrktg',
        ),
        (
            'eyJhbGciOiJIUzsInR5cCI6IkpXVCJ9.'
            'eyJ1c2VyIjoiciBUZXN0NCJ9.'
            'p6MnNJLD5jwTH1C0PvqUb-sp',
        ),
        (
            '',
        ),
    ])
    async def test_connect_invalid(self, token):
        websocket = AsyncMock()
        notify_patched = AsyncMock()
        self.manager.notify_user_list_changed = notify_patched
        with patch('server.connection_manager.JWT_TOKEN_KEY', 'EDAGame$!2021'):
            await self.manager.connect(websocket, token)
        self.assertEqual({}, self.manager.connections)
        websocket.close.assert_called()
        notify_patched.assert_not_called()

    @patch.object(ConnectionManager, 'notify_user_list_changed')
    async def test_remove_user(self, notify_patched):
        self.manager.connections = {'Test Client 1': 'websocket'}
        await self.manager.remove_user('Test Client 1')
        self.assertEqual({}, self.manager.connections)
        notify_patched.assert_called()

    @parameterized.expand([
        (
            {'data': 'Test Message 1'},
            '{"data": "Test Message 1"}',
        ),
    ])
    async def test_broadcast(self, data, expected):
        connection = MagicMock()
        connection.send_text = AsyncMock()
        self.manager.connections = {'Test Client 1': connection}

        await self.manager.broadcast(data)
        connection.send_text.assert_called_with(expected)

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

    @patch.object(ConnectionManager, 'broadcast')
    async def test_notify_user_list_changed(self, broadcast_patched):
        self.manager.connections = {
            'client 1': 'websocket',
            'client 2': 'websocket',
            'client 3': 'websocket',
        }
        await self.manager.notify_user_list_changed()
        broadcast_patched.assert_called_with({
            'event': websocket_events.EVENT_LIST_USERS,
            'data': {
                'users': ['client 1', 'client 2', 'client 3'],
            },
        })
