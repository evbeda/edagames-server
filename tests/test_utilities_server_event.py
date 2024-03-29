import json
import unittest
from unittest.mock import patch, MagicMock, AsyncMock, call

from parameterized import parameterized

from server.utilities_server_event import (
    ServerEvent,
    make_challenge,
    make_move,
    make_penalize,
    make_end_data_for_web,
    make_tournament,
    move,
    start_game,
)
from server.exception import GameIdException

from server.constants import (
    DEBUG_AWAIT,
    DEFAULT_GAME,
    NORMAL_AWAIT,
    TURN_TOKEN,
    TOKEN_COMPARE,
    CHALLENGE_ID,
    GAME_ID,
    GAME_NAME,
    EMPTY_PLAYER,
)


class TestMakeFunctions(unittest.IsolatedAsyncioTestCase):

    @patch('server.utilities_server_event.notify_challenge_to_client')
    @patch('server.utilities_server_event.redis_save')
    async def test_make_challenge(self, mock_save, mock_notify):
        challenge_id = 'test_challenge_id'
        challenger = 'Pedro'
        challenged = ['Pablo']
        players = [challenger, *challenged]
        data_challenge = 'test_data_challenge'
        with patch('server.utilities_server_event.identifier', return_value=challenge_id) as mock_identifier:
            with patch('server.utilities_server_event.data_challenge', return_value=data_challenge) as mock_data:
                debug_mode = False
                await make_challenge(challenger, challenged, DEFAULT_GAME, debug_mode)
                mock_identifier.assert_called_once_with()
                mock_data.assert_called_once_with(players, [challenger], DEFAULT_GAME, debug_mode)
                mock_save.assert_called_once_with(
                    challenge_id,
                    data_challenge,
                    CHALLENGE_ID,
                )
                mock_notify.assert_awaited_once_with(
                    challenged,
                    challenger,
                    challenge_id,
                )

    @parameterized.expand(
        [
            (
                "Enable",
                "JuanBot",
                ["PedroBot"],
                True,
            ),
            (
                "Disable",
                "JuanBot",
                ["PedroBot"],
                False,
            ),
        ]
    )
    async def test_make_challenge_with_debug_mode(
        self,
        name,
        challenger,
        challenged,
        debug_mode,
    ):
        challenge_id = 'test_challenge_id'
        players = [challenger, *challenged]
        data_challenge = json.dumps({
            'players': players,
            'accepted': [challenger],
            'game': DEFAULT_GAME,
            'debug_mode': debug_mode,
        })
        with \
                patch('server.utilities_server_event.identifier', return_value=challenge_id) as mock_identifier, \
                patch('server.utilities_server_event.redis_save') as mock_save, \
                patch('server.utilities_server_event.notify_challenge_to_client') as mock_notify:

            await make_challenge(challenger, challenged, DEFAULT_GAME, debug_mode)
            mock_identifier.assert_called_once()
            mock_save.assert_called_once_with(challenge_id, data_challenge, CHALLENGE_ID,)
            mock_notify.assert_awaited_once_with(
                challenged,
                challenger,
                challenge_id,
            )

    @patch('server.utilities_server_event.identifier')
    @patch('server.utilities_server_event.redis_save')
    @patch('server.utilities_server_event.notify_challenge_to_client')
    async def test_make_challenge_without_debug_mode_param(
        self,
        mock_notify,
        mock_save,
        mock_identifier,
    ):
        challenge_id = 'test_challenge_id'
        mock_identifier.return_value = challenge_id
        players = ["JuanBot", *["PedroBot"]]
        data_challenge = json.dumps({
            'players': players,
            'accepted': ["JuanBot"],
            'game': DEFAULT_GAME,
            'debug_mode': False,
        })
        await make_challenge("JuanBot", ["PedroBot"], DEFAULT_GAME)
        mock_identifier.assert_called_once_with()
        mock_save.assert_called_once_with(challenge_id, data_challenge, CHALLENGE_ID,)
        mock_notify.assert_awaited_once_with(
            ["PedroBot"],
            "JuanBot",
            challenge_id,
        )

    @patch('server.utilities_server_event.notify_your_turn')
    async def test_make_move(self, mock_notify_your_turn):
        game_id = 'test_game_id'
        token_turn = 'c303282d'
        current_player = 'Pablo'
        turn_data = {}
        data = MagicMock(
            game_id=game_id,
            current_player=current_player,
            turn_data=turn_data
        )
        with patch('server.utilities_server_event.next_turn', return_value=token_turn) as mock_next_turn:
            res = await make_move(data)
            mock_next_turn.assert_called_once_with(game_id)
            self.assertEqual(data.turn_data, {GAME_ID: game_id, TURN_TOKEN: token_turn})
            mock_notify_your_turn.assert_awaited_once_with(
                current_player,
                turn_data,
            )
            self.assertEqual(res, token_turn)

    @patch('server.utilities_server_event.make_move')
    @patch('server.utilities_server_event.GRPCAdapterFactory.get_adapter')
    @patch('server.utilities_server_event.asyncio.sleep')
    async def test_make_penalize_called(self, mock_sleep, gadapter_patched, mock_make_move):
        player_1 = 'Pedro'
        player_2 = 'Pablo'
        game_id = '123987'
        turn_token = 'turn_token'
        game = {
            GAME_NAME: DEFAULT_GAME
        }
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
        debug_mode = False
        with patch('server.utilities_server_event.redis_get', side_effect=[turn_token, game]) as mock_get:
            await make_penalize(data, game_name, turn_token, debug_mode,)
            mock_sleep.assert_awaited_once_with(NORMAL_AWAIT)
            mock_get.assert_called()
            gadapter_patched.assert_called_with(DEFAULT_GAME)
            mock_make_move.assert_awaited_once_with(adapter_patched.penalize.return_value)

    @patch.object(ServerEvent, 'game_over')
    @patch('server.utilities_server_event.GRPCAdapterFactory.get_adapter')
    @patch('server.utilities_server_event.asyncio.sleep')
    async def test_make_penalize_called_move(self, mock_sleep, gadapter_patched, mock_game_over):
        player_2 = 'Pablo'
        game_id = '123987'
        turn_token = 'turn_token'
        game = {
            GAME_NAME: 'quoridor'
        }
        data = MagicMock(
            game_id=game_id,
            current_player=player_2,
        )
        game_name = DEFAULT_GAME
        adapter_patched = AsyncMock()
        adapter_patched.penalize.return_value = MagicMock(
            game_id=game_id,
            current_player=EMPTY_PLAYER,
        )
        gadapter_patched.return_value = adapter_patched
        with patch('server.utilities_server_event.redis_get', side_effect=[turn_token, game]) as mock_get:
            debug_mode = False
            await make_penalize(data, game_name, turn_token, debug_mode,)
            mock_sleep.assert_awaited_once_with(NORMAL_AWAIT)
            mock_get.assert_called()
            gadapter_patched.assert_called_with(DEFAULT_GAME)
            mock_game_over.assert_awaited_once_with(adapter_patched.penalize.return_value, game)

    @patch('server.utilities_server_event.make_move')
    @patch('server.utilities_server_event.GRPCAdapterFactory.get_adapter')
    @patch('server.utilities_server_event.asyncio.sleep')
    async def test_make_penalize_not_called(self, mock_sleep, gadapter_patched, mock_move):
        player_1 = 'Pedro'
        game_id = '123987'
        turn_token_1 = 'turn_token_1'
        turn_token_2 = 'turn_token_2'
        data = MagicMock(
            game_id=game_id,
            current_player=player_1,
        )
        game_name = DEFAULT_GAME
        with patch('server.utilities_server_event.redis_get', return_value=turn_token_2) as mock_get:
            debug_mode = False
            await make_penalize(data, game_name, turn_token_1, debug_mode,)
            mock_sleep.assert_awaited_once_with(NORMAL_AWAIT)
            mock_get.assert_awaited_once_with(
                game_id,
                TOKEN_COMPARE,
                player_1,
            )
            gadapter_patched.assert_not_called()
            mock_move.assert_not_called()

    @patch('server.utilities_server_event.asyncio.sleep')
    @patch('server.utilities_server_event.redis_get', return_value='token1')
    async def test_make_penalize_call_in_debug_mode(self, mock_get, mock_sleep):
        player_1 = 'Pedro'
        game_id = '123987'
        data = MagicMock(
            game_id=game_id,
            current_player=player_1,
        )
        game_name = DEFAULT_GAME
        turn_token_1 = 'token2'
        debug_mode = True

        await make_penalize(data, game_name, turn_token_1, debug_mode,)
        mock_sleep.assert_awaited_once_with(DEBUG_AWAIT)
        mock_get.assert_awaited_once_with(game_id, TOKEN_COMPARE, player_1,)

    @patch('server.utilities_server_event.asyncio.sleep')
    @patch('server.utilities_server_event.redis_get', return_value='token1')
    async def test_make_penalize_call_in_normal_mode(self, mock_get, mock_sleep):
        player_1 = 'Pedro'
        game_id = '123987'
        data = MagicMock(
            game_id=game_id,
            current_player=player_1,
        )
        game_name = DEFAULT_GAME
        turn_token_1 = 'token2'
        debug_mode = False

        await make_penalize(data, game_name, turn_token_1, debug_mode,)
        mock_sleep.assert_awaited_once_with(NORMAL_AWAIT)
        mock_get.assert_awaited_once_with(game_id, TOKEN_COMPARE, player_1,)

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
            [('pedro', 1000), ('pablo', 2000)],
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
    def test_make_end_data_for_web(self, data, expected):
        res = make_end_data_for_web(data)
        self.assertEqual(res, expected)


class TestServerEvent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = 'test_client'

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_search_value(self, response):
        value_expected = "c303282d-f2e6-46ca-a04a-35d3d873712d"
        value = 'game_id'
        value_search = await ServerEvent(response, self.client).search_value(value)
        self.assertEqual(value_search, value_expected)

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {}},),
    ])
    async def test_search_value_error(self, response):
        with patch('server.utilities_server_event.notify_error_to_client') as notify_patched:
            value = 'game_id'
            await ServerEvent(response, self.client).search_value(value)
            notify_patched.assert_called_once_with(self.client, str(GameIdException))

    @patch('asyncio.create_task')
    @patch('server.utilities_server_event.make_penalize', new_callable=MagicMock, return_value='ret_penalize')
    @patch('server.utilities_server_event.make_move', return_value='test_token')
    async def test_move(
        self,
        mock_make_move,
        mock_make_penalize,
        mock_asyncio,
    ):
        data = MagicMock(
            game_id='123987',
            current_player='Pedro',
            turn_data={},
        )
        game_name = DEFAULT_GAME
        debug_mode = True
        await move(data, game_name, debug_mode,)
        mock_make_move.assert_awaited_once_with(data)
        mock_make_penalize.assert_called_once_with(data, game_name, 'test_token', debug_mode,)
        mock_asyncio.assert_called_once_with('ret_penalize')

    @patch('server.utilities_server_event.notify_end_game_to_web')
    @patch('server.utilities_server_event.notify_end_game_to_client')
    @patch('server.utilities_server_event.next_turn')
    async def test_game_over(self, mock_next, mock_notify_end_to_client, mock_notify_end_to_web):
        players = ['Pedro', 'Pablo']
        game_data = {
            'players': players,
            'name': DEFAULT_GAME,
        }
        game_id = 'f34i3f'
        turn_data = {"turn_data": "turn_data"}
        data = MagicMock(
            game_id=game_id,
            turn_data=turn_data,
        )
        test_end_data = 'test_end_data'
        with patch('server.utilities_server_event.make_end_data_for_web', return_value=test_end_data) as mock_end_data:
            await ServerEvent({}, self.client).game_over(data, game_data)
            mock_next.assert_called_once_with(game_id)
            mock_end_data.assert_called_once_with(turn_data)
            mock_notify_end_to_client.assert_called_once_with(players, turn_data)
            mock_notify_end_to_web.assert_called_once_with(game_id, None, test_end_data)

    @patch('server.utilities_server_event.move')
    @patch('server.utilities_server_event.redis_save')
    async def test_start_game(self, mock_save, mock_move):
        game_id = 'asd123'
        game_data = {
            'game': DEFAULT_GAME,
            'players': ['client1', 'clint2'],
            'debug_mode': False,
        }
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as g_adapter_patched:
            adapter_patched = AsyncMock()
            adapter_patched.create_game.return_value = MagicMock(
                game_id=game_id,
                current_player='client1',
                turn_data={},
                play_data={},
            )
            g_adapter_patched.return_value = adapter_patched
            await start_game(game_data)
            g_adapter_patched.assert_called_with(DEFAULT_GAME)
            mock_save.assert_called_once_with(
                game_id,
                game_data,
                GAME_ID,
            )
            mock_move.assert_awaited_once_with(
                adapter_patched.create_game.return_value,
                DEFAULT_GAME,
                False,
            )

    @patch('server.utilities_server_event.start_game')
    async def test_make_tournament(self, start_game_patched):
        tournament_id = '123456'
        games = [['Player 1', 'Player 2'], ['Player 3', 'Player 1']]
        await make_tournament(tournament_id, games, DEFAULT_GAME)
        calls = [call({
            'tournament_id': tournament_id,
            'players': players,
            'name': DEFAULT_GAME,
            'debug_mode': False,
        }) for players in games]
        start_game_patched.assert_has_calls(calls)
