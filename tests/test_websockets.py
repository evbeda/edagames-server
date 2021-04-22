import unittest
from unittest.mock import AsyncMock, patch
from server.connection_manager import ConnectionManager
from server.websockets import notify_error_to_client
import server.websocket_events as websocket_events


class TestWebsockets(unittest.IsolatedAsyncioTestCase):
    @patch.object(ConnectionManager, 'send', new_callable=AsyncMock)
    async def test_notify_error_to_client(self, send_patched):
        client = 'User 1'
        error = 'message error'
        await notify_error_to_client(
            client,
            error,
        )
        send_patched.assert_called_with(
            client,
            websocket_events.EVENT_SEND_ERROR,
            {
                'Error': error,
            },
        )
