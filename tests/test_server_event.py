import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from parameterized import parameterized

from server.game import Game
from server.server_event import (
    AcceptChallenge,
    Movements,
    ListUsers,
    Challenge,
    AbortGame,
)
from server.utilities_server_event import (
    MovesActions,
    EndActions,
)

from server.constants import (
    LAST_PLAYER,
    OPPONENT,
    CHALLENGE_ID,
    DEFAULT_GAME,
)


class TestServerEvent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.uuid = 'c303282d-f2e6-46ca-a04a-35d3d873712d'
        with patch('uuid.uuid4', return_value=self.uuid):
            self.game = Game(['player1', 'player2'])

    @patch.object(AcceptChallenge, 'start_game')
    @patch('server.server_event.get_string', return_value='data_from_redis', new_callable=AsyncMock)
    @patch.object(MovesActions, 'search_value', return_value='challenge_id_from_request')
    async def test_accept_challenge(self, mock_search, mock_get, mock_start):
        data = {"action": "accept_challenge", "data": {"challenge_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}}
        client = 'Test Client 1'
        json_to_python = 'python data'
        with patch('json.loads', return_value=json_to_python) as mock_json:
            await AcceptChallenge(data, client).run()
            mock_search.assert_called_with(data, client, CHALLENGE_ID)
            mock_get.assert_called_with('challenge_id_from_request', client, CHALLENGE_ID)
            mock_start.assert_called_with(json_to_python)
            mock_json.assert_called_with('data_from_redis')

    @patch.object(MovesActions, 'make_move')
    async def test_start_game(self, mock_make_move):
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as g_adapter_patched:
            adapter_patched = AsyncMock()
            game_id = '12321312'
            adapter_patched.create_game.return_value = MagicMock(
                game_id=game_id,
                current_player='Juan',
                turn_data={},
            )
            g_adapter_patched.return_value = adapter_patched
            game = {'name': DEFAULT_GAME, 'players': '[client1 ,clint1]'}
            await AcceptChallenge({}, 'client').start_game(game)
            g_adapter_patched.assert_called_with(DEFAULT_GAME)
            mock_make_move.assert_called_once_with(
                game,
                game_id,
                adapter_patched.create_game.return_value,
            )

    def my_side_effect(*args):
        if args[0] == '1':
            return True
        else:
            return False

    @parameterized.expand([
        (
            {
                "action": "accept_challenge",
                "data": {"turn_token": "303282d-f2e6-46ca-a04a-35d3d873712d", "board_id": 'c303282d'}
            },
        ),
    ])
    async def test_Movements(self, data):
        client = 'Test Client 1'
        # game_id = 'c303282d'
        # turn_token = '303282d-f2e6-46ca-a04a-35d3d873712d'
        # game = {'name': DEFAULT_GAME, 'players': '[client1 ,clint1]'}
        with patch.object(MovesActions, 'search_value', return_value='value') as mock_search:
            with patch("server.server_event.get_string", return_value='value') as mock_get:
                with patch('json.loads', return_value='json_value') as mock_json:
                    with patch.object(Movements, 'execute_action', return_value='value') as mock_execute:
                        await Movements(data, client).run()
                        mock_search.assert_called()
                        mock_get.assert_called()
                        mock_json.asseer_called()
                        mock_execute.assert_called()

    async def test_list_users(self):
        data = {'action': 'list_users'}
        client = 'User 1'
        users = ['User 1', 'User 2', 'User 3']
        with patch('server.server_event.notify_user_list_to_client', new_callable=AsyncMock) as notify_patched,\
                patch('server.server_event.manager') as manager_patched:
            manager_patched.connections.keys.return_value = users
            await ListUsers(data, client).run()
            notify_patched.assert_called_with(client, users)

    @patch.object(MovesActions, 'make_move')
    async def test_execute_action(self, mock_make_move):
        turn_data = {'game_id': 'fjj02', 'player_1': 'Mark', 'score_1': 1000}
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as Gadapter_patched,\
                patch.object(Movements, 'log_action') as log_patched:
            adapter_patched = AsyncMock()
            adapter_patched.execute_action.return_value = MagicMock(
                turn_data=turn_data,
                current_player='Mark',
            )
            Gadapter_patched.return_value = adapter_patched
            game = {'name': DEFAULT_GAME, 'players': '[client1 ,clint1]'}
            await Movements({}, 'client').execute_action(game)
            Gadapter_patched.assert_called_with(self.game.name)
            mock_make_move.assert_awaited_once_with(
                game,
                adapter_patched.execute_action.return_value,
            )
            log_patched.assert_awaited_once_with(
                self.game,
                adapter_patched.execute_action.return_value,
            )

    @patch.object(EndActions, 'game_over')
    async def test_movements_end_game(self, mock_game_over):
        client = 'Test Client'
        turn_data = {'game_id': 'fjj02', 'player_1': 'Mark', 'score_1': 1000}
        with patch('server.server_event.GRPCAdapterFactory.get_adapter') as g_adapter_patched,\
                patch.object(Movements, 'log_action'):
            adapter_patched = AsyncMock()
            adapter_patched.execute_action.return_value = MagicMock(
                turn_data=turn_data,
                current_player=LAST_PLAYER,
            )
            g_adapter_patched.return_value = adapter_patched
            game = {'name': DEFAULT_GAME, 'players': '[client1 ,clint1]'}
            await Movements({}, client).execute_action(game)
            mock_game_over.assert_awaited_once_with(
                game,
                adapter_patched.execute_action.return_value
            )

    @patch('server.server_event.save_string')
    @patch('json.dumps')
    async def test_movements_log_action(self, json_dumps_patched, save_patched):
        game = MagicMock(game_id='test-0000-00000001')
        data = MagicMock(
            previous_player='Player1',
            turn_data={
                'board_id': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'action': 'move',
                'from_row': 3,
                'from_col': 4,
                'to_row': 4,
                'to_col': 4,
            },
        )
        turn_data_json = (
            '{"turn": "Player1", "data": {'
            '"board_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", '
            '"action": "move", '
            '"from_row": 3, '
            '"from_col": 4, '
            '"to_row": 4, '
            '"to_col": 4'
            '}}'
        )
        json_dumps_patched.return_value = turn_data_json
        await Movements({}, 'client').log_action(game, data)
        save_patched.assert_called_once_with(
            'l_test-0000-00000001',
            turn_data_json,
        )

    @patch('server.server_event.notify_challenge_to_client')
    @patch.object(MovesActions, 'search_value', return_value='test_opponent')
    @patch('server.server_event.save_string')
    async def test_challenge(self, mock_save, mock_search, mock_notify_challenge):
        client = 'Test Client'
        opponent = 'test_opponent'
        challenge_data = {'opponent': opponent}
        response = {'data': challenge_data}
        to_json = '''{ players: [player_1, player_2]}'''
        with patch('uuid.uuid4', return_value=self.uuid):
            with patch('server.server_event.data_challenge', return_value=to_json) as mock_data:
                await Challenge(response, client).run()
                mock_data.assert_called_once_with([client, opponent])
                mock_save.assert_called_once_with('c_' + self.uuid, to_json)
                mock_search.assert_awaited_once_with(response, client, OPPONENT)
                mock_notify_challenge.assert_awaited_once_with(opponent, client, self.uuid)

    @parameterized.expand([
        (
            {
                "action": "accept_challenge",
                "data": {"turn_token": "303282d-f2e6-46ca-a04a-35d3d873712d", "board_id": 'c303282d'}
            },
        ),
    ])
    async def test_abort_game(self, data):
        client = 'Test Client'
        with patch.object(MovesActions, 'search_value', return_value='10') as mock_search:
            with patch('server.server_event.get_string', return_value='10') as mock_get:
                with patch.object(AbortGame, 'end_game', return_value='10') as mock_end:
                    await AbortGame(data, client).run()
                    mock_search.assert_any_call(data, client, 'board_id')
                    mock_search.assert_any_call(data, client, 'turn_token')
                    self.assertEqual(mock_search.call_count, 2)
                    mock_get.assert_awaited()
                    mock_end.assert_awaited()

    @patch.object(EndActions, 'game_over')
    async def test_abort_game_end_game(self, mock_game_over):
        client = 'client'
        game_id = 'asd123'
        with patch('server.server_event.GRPCAdapterFactory.get_adapter') as g_adapter_patched:
            adapter_patched = AsyncMock()
            adapter_patched.end_game.return_value = MagicMock(
                current_player=LAST_PLAYER,
                turn_data={'player_1': 'Mark', 'score_1': 1000},
                play_data={'state': 'game_over'}
            )
            g_adapter_patched.return_value = adapter_patched
            game = {'name': DEFAULT_GAME, 'players': '[client1 ,clint1]'}
            await AbortGame({}, client).end_game(game, game_id)
            mock_game_over.assert_awaited_once_with(
                game,
                adapter_patched.end_game.return_value
            )
