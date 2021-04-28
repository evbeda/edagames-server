import unittest
from unittest.mock import AsyncMock, patch

from server.connection_manager import ConnectionManager
from server.websockets import (
    notify_error_to_client,
    notify_challenge_to_client,
    notify_your_turn,
    notify_user_list_to_client,
)

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

    @patch.object(ConnectionManager, 'send', new_callable=AsyncMock)
    async def test_notify_your_turn(self, send_patched):
        challenge_sender = 'User 1'
        data = {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}
        await notify_your_turn(
            challenge_sender,
            data
        )
        send_patched.assert_called_with(
            challenge_sender,
            websocket_events.EVENT_SEND_YOUR_TURN,
            data
        )

    @patch.object(ConnectionManager, 'send', new_callable=AsyncMock)
    async def test_notify_user_list_to_client(self, send_patched):
        client = 'User 1'
        users = ['User 1', 'User 2', 'User 3']
        await notify_user_list_to_client(client, users)
        send_patched.assert_called_with(
            client,
            websocket_events.EVENT_LIST_USERS,
            {
                'users': users,
            },
        )
