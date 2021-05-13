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
    DEFAULT_GAME,
    TIME_SLEEP,
    TURN_TOKEN,
    PREFIX_TURN_TOKEN,
)


class TestMovesActions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = Game(['player1', 'player2'])

    @patch('server.utilities_server_event.move')
    @patch('server.utilities_server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock)
    @patch('server.utilities_server_event.get_string', new_callable=AsyncMock, return_value=None)
    async def test_penalize_called(self, get_string_patch, gadapter_patched, mock_move):
        player_1 = 'Pedro'
        player_2 = 'Pablo'
        game_id = '123987'
        data = MagicMock(
            game_id=game_id,
            current_player=player_1,
        )
        game_name = DEFAULT_GAME
        adapter_patched = AsyncMock()
        adapter_patched.penalize.return_value = MagicMock(
            game_id=game_id,
            current_player=player_2,
        )
        gadapter_patched.return_value = adapter_patched
        with patch('server.utilities_server_event.asyncio.sleep') as sleep_pached:
            await penalize(data, game_name)
            sleep_pached.assert_called_with(TIME_SLEEP)
            get_string_patch.assert_awaited_once_with(
                f'{PREFIX_TURN_TOKEN}{game_id}',
                player_1,
                TURN_TOKEN,
            )
            gadapter_patched.assert_called_with(DEFAULT_GAME)
            mock_move.assert_awaited_once_with(adapter_patched.penalize.return_value)

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
    @patch('server.utilities_server_event.move')
    async def test_make_move(
        self,
        mock_move,
        mock_asyncio,
        mock_penalize,
    ):
        data = MagicMock(
            game_id='123987',
            current_player='Juan',
            turn_data={},
        )
        game = {'players': ['Pedro', 'Pablo'], 'name': DEFAULT_GAME}
        game_id = '123987'
        await MovesActions.make_move(self, game, data, game_id)
        mock_move.assert_awaited_once_with(game_id, data)
        mock_penalize.assert_called_once_with(game_id, DEFAULT_GAME)
        mock_asyncio.assert_called_once_with(10)

    @patch('server.utilities_server_event.notify_your_turn', new_callable=AsyncMock)
    @patch('server.utilities_server_event.next_turn')
    async def test_move(self, mock_next_turn, mock_notify_your_turn):
        data = MagicMock(
            game_id='123987',
            current_player='Juan',
            turn_data={},
        )
        token_turn = 'c303282d'
        mock_next_turn.return_value = token_turn
        test_game_id = 'fk340of3'
        game_id = test_game_id
        await move(game_id, data)
        self.assertEqual(data.turn_data, {'board_id': test_game_id, 'turn_token': token_turn})
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
        game = {'players': ['Pedro', 'Pablo'], 'name': DEFAULT_GAME}
        test_end_data = [('pablo', 2000), ('pedro', 1000)]
        with patch('server.utilities_server_event.end_data_for_web', return_value=test_end_data) as mock_end_data:
            await EndActions.game_over(self, game, data)
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
    def test_end_data_for_web(self, data, expected):
        res = end_data_for_web(data)
        self.assertEqual(res, expected)
