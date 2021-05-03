import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from parameterized import parameterized
import asyncio

from server.game import Game, games
from server.server_event import (
    AcceptChallenge,
    Movements,
    ListUsers,
)
from server.constants import (
    GAME_STATE_ACCEPTED,
    GAME_STATE_ENDED,
    LAST_PLAYER,
)


class TestServerEvent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        with patch(
            'uuid.uuid4',
            return_value='c303282d-f2e6-46ca-a04a-35d3d873712d'
        ):
            self.game = Game(['player1', 'player2'])

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_accept_challenge(self, data):
        client = 'Test Client 1'
        with patch('server.server_event.notify_error_to_client', new_callable=AsyncMock):
            games.append(self.game)
            with patch.object(AcceptChallenge, 'start_game') as mock_run:
                await AcceptChallenge(data, client).run()
                mock_run.assert_called()

    @patch('server.server_event.notify_your_turn')
    @patch.object(Game, 'next_turn')
    async def test_start_game(self, mock_next_turn, n_your_turn):
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as g_adapter_patched:
            with patch.object(AcceptChallenge, 'penalize') as mock_penalize:
                adapter_patched = AsyncMock()
                adapter_patched.create_game.return_value = MagicMock(
                    game_id='123987',
                    current_player='Juan',
                    turn_data={},
                )
                g_adapter_patched.return_value = adapter_patched
                self.game.turn_token = 'asd123'
                await AcceptChallenge({}, 'client').start_game(self.game)
                mock_penalize.assert_called()
                g_adapter_patched.assert_called_with(self.game.name)
                mock_next_turn.assert_called_with()
                n_your_turn.assert_called_with('Juan', {'turn_token': 'asd123'})
                self.assertEqual(self.game.state, GAME_STATE_ACCEPTED)

    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"turn_token": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_Movements(self, data):
        client = 'Test Client 1'
        with patch('server.server_event.notify_error_to_client', new_callable=AsyncMock):
            with patch('server.server_event.notify_your_turn', new_callable=AsyncMock):
                with patch('asyncio.create_task', new_callable=MagicMock):
                    game = Game(['mov_player1', 'mov_player2'])
                    game.timer = asyncio.create_task()
                    game.turn_token = 'c303282d-f2e6-46ca-a04a-35d3d873712d'
                    games.append(game)
                    with patch.object(Movements, 'execute_action') as start_patched:
                        await Movements(data, client).run()
                        start_patched.assert_called()

    async def test_list_users(self):
        data = {'action': 'list_users'}
        client = 'User 1'
        users = ['User 1', 'User 2', 'User 3']

        with patch('server.server_event.notify_user_list_to_client', new_callable=AsyncMock) as notify_patched,\
                patch('server.server_event.manager') as manager_patched:
            manager_patched.connections.keys.return_value = users
            await ListUsers(data, client).run()
            notify_patched.assert_called_with(client, users)

    async def test_execute_action(self):
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as Gadapter_patched:
            with patch('server.server_event.notify_your_turn') as notify_patched:
                adapter_patched = AsyncMock()
                adapter_patched.execute_action.return_value = MagicMock()
                Gadapter_patched.return_value = adapter_patched
                await Movements({}, 'client').execute_action(self.game)
                Gadapter_patched.assert_called_with(self.game.name)
                notify_patched.assert_called()

    @patch.object(Movements, 'end_data_for_web', return_value={'player_1': 1000})
    @patch('server.server_event.notify_end_game_to_web')
    @patch('server.server_event.notify_end_game_to_client')
    async def test_end_game(self, mock_client, mock_web, mock_end_data):
        client = 'Test Client'
        turn_data = {'game_id': 'fjj02', 'player_1': 'Mark', 'score_1': 1000}
        end_data = {'player_1': 1000}
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as g_adapter_patched:
            adapter_patched = AsyncMock()
            adapter_patched.execute_action.return_value = MagicMock(
                turn_data=turn_data,
                current_player=LAST_PLAYER,
            )
            g_adapter_patched.return_value = adapter_patched
            await Movements({}, client).execute_action(self.game)
            mock_client.assert_called_once_with(
                self.game.players,
                turn_data,
            )
            mock_web.assert_called_once_with(
                self.game.game_id,
                end_data,
            )
            mock_end_data.assert_called_once_with(turn_data)
            self.assertEqual(self.game.state, GAME_STATE_ENDED)

    @parameterized.expand([
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
    ])
    async def test_end_data_for_web(self, data, expected):
        client = 'Test Client'
        res = await Movements({}, client).end_data_for_web(data)
        self.assertEqual(res, expected)

    async def test_penalize(self):
        with patch('server.server_event.GRPCAdapterFactory.get_adapter', new_callable=AsyncMock) as Gadapter_patched:
            with patch('server.server_event.notify_your_turn') as notify_patched:
                adapter_patched = AsyncMock()
                adapter_patched.penalize.return_value = MagicMock()
                Gadapter_patched.return_value = adapter_patched
                with patch('server.server_event.asyncio.sleep') as sleep_pached:
                    await AcceptChallenge({}, 'client').penalize(self.game)
                    sleep_pached.assert_called()
                    Gadapter_patched.assert_called_with(self.game.name)
                    notify_patched.assert_called()
