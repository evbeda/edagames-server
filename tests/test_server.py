import unittest
from server.connection_manager import ConnectionManager
import server.server as server
from unittest.mock import patch, AsyncMock
import starlette


class TestServer(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        ConnectionManager.instance = AsyncMock()
        ConnectionManager.connection_type = 'websocket'

    def tearDown(self) -> None:
        ConnectionManager.instance = None
        ConnectionManager.connection_type = None

    async def test_session_open_close(self):
        websocket = AsyncMock()
        websocket.receive_text.side_effect = starlette.websockets.WebSocketDisconnect()

        with patch('server.server.ConnectionManager.instance') as manager_patched:
            manager_patched.connect = AsyncMock()
            manager_patched.remove_user = AsyncMock()
            manager_patched.connect.return_value = 'User 1'
            await server.session(websocket, 'token')
            manager_patched.connect.assert_called_with(websocket, 'token')
            manager_patched.remove_user.assert_called_with('User 1')
