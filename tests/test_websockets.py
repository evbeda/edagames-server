import unittest
from unittest.mock import AsyncMock, patch
from server.connection_manager import ConnectionManager
from server.websockets import notify_error_to_client, notify_challenge_to_client, notify_game_created
import server.websocket_events as websocket_events
import server.web_urls as web_urls
import json


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

    @patch('requests.post')
    def test_notify_game_created(self, post_patched):
        notify_game_created(
            '00000000-0000-0000-0000-000000000001',
            '123e4567-e89b-12d3-a456-426614174000',
        )

        post_patched.assert_called_with(
            web_urls.GAME_URL,
            json=json.dumps({
                'challenge_id': '00000000-0000-0000-0000-000000000001',
                'game_id': '123e4567-e89b-12d3-a456-426614174000',
            })
        )

    @patch.object(ConnectionManager, 'send', new_callable=AsyncMock)
    async def test_notify_challenge_to_client(self, send_patched):
        challenge_sender = 'User 1'
        challenge_receiver = 'User 2'
        test_game_id = '00000000-0000-0000-0000-000000000001'
        await notify_challenge_to_client(
            challenge_receiver,
            challenge_sender,
            test_game_id,
        )
        send_patched.assert_called_with(
            challenge_receiver,
            websocket_events.EVENT_SEND_CHALLENGE,
            {
                'opponent': challenge_sender,
                'game_id': test_game_id,
            },
        )
