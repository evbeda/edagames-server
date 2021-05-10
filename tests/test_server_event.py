import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from parameterized import parameterized
import asyncio

from server.game import Game, games
from server.server_event import (
    AcceptChallenge,
    Movements,
    ListUsers,
    Challenge,
)
from server.utilities_server_event import (
    MovesActions,
    EndActions,
)

from server.constants import (
    GAME_STATE_ACCEPTED,
    LAST_PLAYER,
    OPPONENT,
)


class TestServerEvent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.uuid = 'c303282d-f2e6-46ca-a04a-35d3d873712d'
        with patch(
            'uuid.uuid4',
            return_value=self.uuid
        ):
            self.game = Game(['player1', 'player2'])

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"challenge_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_accept_challenge(self, data):
        client = 'Test Client 1'
        games.append(self.game)
        with patch.object(AcceptChallenge, 'start_game') as mock_run:
            await AcceptChallenge(data, client).run()
            mock_run.assert_called()

    @patch.object(MovesActions, 'make_move')
    async def test_start_game(self, mock_make_move):
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as g_adapter_patched:
            adapter_patched = AsyncMock()
            game_id = '123987'
            adapter_patched.create_game.return_value = MagicMock(
                game_id=game_id,
                current_player='Juan',
                turn_data={},
            )
            g_adapter_patched.return_value = adapter_patched
            self.game.turn_token = 'asd123'
            await AcceptChallenge({}, 'client').start_game(self.game)
            self.assertEqual(self.game.state, GAME_STATE_ACCEPTED)
            g_adapter_patched.assert_called_with(self.game.name)
            mock_make_move.assert_called_once_with(
                self.game,
                adapter_patched.create_game.return_value,
            )
            self.assertEqual(self.game.game_id, game_id)

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"turn_token": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_Movements(self, data):
        client = 'Test Client 1'
        with patch('asyncio.create_task', new_callable=MagicMock):
            game = Game(['mov_player1', 'mov_player2'])
            game.timer = asyncio.create_task()
            game.turn_token = 'c303282d-f2e6-46ca-a04a-35d3d873712d'
            games.append(game)
            with patch.object(Movements, 'execute_action') as start_patched:
                await Movements(data, client).run()
                start_patched.assert_called_with(game)

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
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as Gadapter_patched:
            adapter_patched = AsyncMock()
            adapter_patched.execute_action.return_value = MagicMock(
                turn_data=turn_data,
                current_player='Mark',
            )
            Gadapter_patched.return_value = adapter_patched
            await Movements({}, 'client').execute_action(self.game)
            Gadapter_patched.assert_called_with(self.game.name)
            mock_make_move.assert_awaited_once_with(
                self.game,
                adapter_patched.execute_action.return_value,
            )

    @patch.object(EndActions, 'game_over')
    async def test_end_game(self, mock_game_over):
        client = 'Test Client'
        turn_data = {'game_id': 'fjj02', 'player_1': 'Mark', 'score_1': 1000}
        with patch('server.server_event.GRPCAdapterFactory.get_adapter') as g_adapter_patched:
            adapter_patched = AsyncMock()
            adapter_patched.execute_action.return_value = MagicMock(
                turn_data=turn_data,
                current_player=LAST_PLAYER,
            )
            g_adapter_patched.return_value = adapter_patched
            await Movements({}, client).execute_action(self.game)
            mock_game_over.assert_awaited_once_with(
                self.game,
                adapter_patched.execute_action.return_value
            )

    @patch('server.server_event.notify_challenge_to_client')
    @patch.object(MovesActions, 'search_value', return_value='test_opponent')
    async def test_challenge(self, mock_search, mock_notify_challenge):
        client = 'Test Client'
        opponent = 'test_opponent'
        challenge_data = {'opponent': opponent}
        response = {'data': challenge_data}
        q_games = len(games)
        with patch('uuid.uuid4', return_value=self.uuid):
            await Challenge(response, client).run()
            mock_search.assert_awaited_once_with(response, client, OPPONENT)
            mock_notify_challenge.assert_awaited_once_with(opponent, client, self.uuid)
            self.assertEqual(q_games + 1, len(games))
