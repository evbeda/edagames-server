import unittest
from unittest.mock import patch, AsyncMock, MagicMock

from server.utilities_server_event import penalize
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
