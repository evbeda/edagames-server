import unittest
from parameterized import parameterized
from unittest.mock import MagicMock, AsyncMock
from server.connection_manager import ConnectionManager


class TestServer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.manager = ConnectionManager()

    @parameterized.expand([
        (
            'Test Client 1',
        )
    ])
    async def test_connect(self, client):
        websocket = MagicMock()
        websocket.accept = AsyncMock()

        await self.manager.connect(websocket, client)
        websocket.accept.assert_called()

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
