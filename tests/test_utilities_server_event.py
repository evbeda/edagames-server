import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from parameterized import parameterized

from server.utilities_server_event import (
    penalize,
    MovesActions,
)
from server.game import Game
from server.exception import GameIdException

from server.constants import TIME_SLEEP


class TestUtilitiesServerEvent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = Game(['player1', 'player2'])

    @patch('server.utilities_server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock)
    @patch('server.utilities_server_event.notify_your_turn', new_callable=AsyncMock)
    @patch('uuid.uuid4', return_value='c303282d-f2e6-46ca-a04a-35d3d873712d')
    async def test_penalize(self, uuiid_mock, notify_patched, gadapter_patched):
        data = MagicMock(
            game_id='123987',
            current_player='Juan',
            turn_data={'turn_token': 'c303282d-f2e6-46ca-a04a-35d3d873712d'},
        )
        adapter_patched = AsyncMock()
        adapter_patched.penalize.return_value = MagicMock(
            game_id='123987',
            current_player='Juan',
            turn_data={},
        )
        gadapter_patched.return_value = adapter_patched
        with patch('server.utilities_server_event.asyncio.sleep') as sleep_pached:
            await penalize(self.game)
            sleep_pached.assert_called_with(TIME_SLEEP)
            gadapter_patched.assert_called_with(self.game.name)
            notify_patched.assert_awaited_once_with(
                data.current_player,
                data.turn_data,
            )

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_search_value(self, response):
        client = 'User 1'
        value = 'game_id'
        value_search = await MovesActions.search_value(response, client, value)
        value_expected = "c303282d-f2e6-46ca-a04a-35d3d873712d"
        self.assertEqual(value_search, value_expected)

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {}},),
    ])
    async def test_search_value_error(self, response):
        with patch('server.utilities_server_event.notify_error_to_client') as notify_patched:
            client = 'User 1'
            value = 'game_id'
            await MovesActions.search_value(response, client, value)
            notify_patched.assert_called_with(client, str(GameIdException))

    @patch('server.utilities_server_event.penalize', new_callable=MagicMock, return_value=10)
    @patch('asyncio.create_task')
    @patch('server.utilities_server_event.notify_your_turn', new_callable=AsyncMock)
    async def test_make_move(
        self,
        mock_notify_your_turn,
        mock_asyncio,
        mock_penalize,
    ):
        data = MagicMock(
            game_id='123987',
            current_player='Juan',
            turn_data={},
        )
        uuid_value = 'c303282d'
        with patch('uuid.uuid4', return_value=uuid_value):
            await MovesActions.make_move(self, self.game, data)
            self.assertEqual(data.turn_data, {'turn_token': uuid_value})
            mock_notify_your_turn.assert_awaited_once_with(
                data.current_player,
                data.turn_data,
            )
            mock_penalize.assert_called_once_with(self.game)
            mock_asyncio.assert_called_once_with(10)
