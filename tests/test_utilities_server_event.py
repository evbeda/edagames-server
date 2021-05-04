import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from parameterized import parameterized

from server.utilities_server_event import penalize, search_value
from server.game import Game

from server.constants import TIME_SLEEP


class TestUtilitiesServerEvent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = Game(['player1', 'player2'])

    @patch('server.utilities_server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock)
    async def test_penalize(self, gadapter_patched):
        with patch('server.utilities_server_event.notify_your_turn') as notify_patched:
            adapter_patched = AsyncMock()
            adapter_patched.penalize.return_value = MagicMock()
            gadapter_patched.return_value = adapter_patched
            with patch('server.utilities_server_event.asyncio.sleep') as sleep_pached:
                await penalize(self.game)
                sleep_pached.assert_called_with(TIME_SLEEP)
                gadapter_patched.assert_called_with(self.game.name)
                notify_patched.assert_called()

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_search_value(self, response):
        client = 'User 1'
        value = 'game_id'
        value_search = await search_value(response, client, value)
        value_expected = "c303282d-f2e6-46ca-a04a-35d3d873712d"
        self.assertEqual(value_search, value_expected)

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {}},),
    ])
    async def test_search_value_error(self, response):
        with patch('server.utilities_server_event.notify_error_to_client') as notify_patched:
            client = 'User 1'
            value = 'game_id'
            await search_value(response, client, value)
            notify_patched.assert_called()
