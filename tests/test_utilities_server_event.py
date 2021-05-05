import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from parameterized import parameterized

from server.utilities_server_event import (
    MovesActions,
    EndActions,
    penalize,
    end_data_for_web,
    move,
)
from server.game import Game
from server.exception import GameIdException

from server.constants import (
    TIME_SLEEP,
    GAME_STATE_ENDED,
)


class TestMovesActions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = Game(['player1', 'player2'])

    @patch('server.utilities_server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock)
    @patch('server.utilities_server_event.notify_your_turn', new_callable=AsyncMock)
    @patch('uuid.uuid4', return_value='c303282d-f2e6-46ca-a04a-35d3d873712d')
    async def test_penalize(self, uuiid_mock, notify_patched, gadapter_patched):
        data = MagicMock(
            game_id='123987',
            current_player='Juan',
            turn_data={'turn_token': 'c303282d-f2e6-46ca-a04a-35d3d873712d', 'board_id': None},
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
        value_search = await MovesActions.search_value(self, response, client, value)
        value_expected = "c303282d-f2e6-46ca-a04a-35d3d873712d"
        self.assertEqual(value_search, value_expected)

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {}},),
    ])
    async def test_search_value_error(self, response):
        with patch('server.utilities_server_event.notify_error_to_client') as notify_patched:
            client = 'User 1'
            value = 'game_id'
            await MovesActions.search_value(self, response, client, value)
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
            self.assertEqual(data.turn_data, {'board_id': self.game.game_id, 'turn_token': uuid_value})
            mock_notify_your_turn.assert_awaited_once_with(
                data.current_player,
                data.turn_data,
            )
            mock_penalize.assert_called_once_with(self.game)
            mock_asyncio.assert_called_once_with(10)

    @patch('server.utilities_server_event.notify_your_turn', new_callable=AsyncMock)
    async def test_move(self, mock_notify_your_turn):
        data = MagicMock(
            game_id='123987',
            current_player='Juan',
            turn_data={},
        )
        uuid_value = 'c303282d'
        test_game_id = 'fk340of3'
        self.game.game_id = test_game_id
        with patch('uuid.uuid4', return_value=uuid_value):
            await move(self.game, data)
            self.assertEqual(data.turn_data, {'board_id': test_game_id, 'turn_token': uuid_value})
            mock_notify_your_turn.assert_awaited_once_with(
                data.current_player,
                data.turn_data,
            )


class TestEndActions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = Game(['Pedro', 'Pablo'])

    @patch('server.utilities_server_event.notify_end_game_to_web')
    @patch('server.utilities_server_event.notify_end_game_to_client')
    async def test_game_over(
        self,
        mock_notify_end_to_client,
        mock_notify_end_to_web,
    ):
        test_data = {
            'player_1': 'Pedro',
            'score_1': 1000,
            'player_2': 'Pablo',
            'score_2': 2000,
        }
        data = MagicMock(
            game_id='f34i3f',
            current_player='',
            turn_data=test_data,
        )
        test_end_data = [('pablo', 2000), ('pedro', 1000)]
        with patch('server.utilities_server_event.end_data_for_web', return_value=test_end_data) as mock_end_data:
            await EndActions.game_over(self, self.game, data)
            self.assertEqual(self.game.state, GAME_STATE_ENDED)
            mock_notify_end_to_client.assert_called_once_with(
                self.game.players,
                data.turn_data
            )
            mock_end_data.assert_called_once_with(data.turn_data)
            mock_notify_end_to_web.assert_called_once_with(
                self.game.game_id,
                test_end_data
            )

    @parameterized.expand([
        # Dicctionary in order
        (
            {
                'player_1': 'pedro',
                'player_2': 'pablo',
                'game_id': 'f932jf',
                'score_1': 1000,
                'score_2': 2000,
                'remaining_moves': 130,
            },
            [('pablo', 2000), ('pedro', 1000)],
        ),
        # untidy players in dicctionary
        (
            {
                'player_2': 'pablo',
                'player_1': 'pedro',
                'game_id': 'f932jf',
                'score_1': 1000,
                'score_2': 2000,
                'remaining_moves': 130,
            },
            [('pablo', 2000), ('pedro', 1000)],

        ),
    ])
    async def test_end_data_for_web(self, data, expected):
        res = await end_data_for_web(data)
        self.assertEqual(res, expected)
