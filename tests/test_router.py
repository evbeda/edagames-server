import unittest
from unittest.mock import patch
from parameterized import parameterized
from httpx import AsyncClient
import json

from server.server import app, manager

from server.constants import DEFAULT_GAME


class TestRouter(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        (
            "Ana",
            ["Pepe"],
            200,
        ),
        (
            "Ana",
            ["Pepe"],
            200,
        ),
    ])
    async def test_challenge(self, challenger, challenged, status):
        data = {
            "challenger": challenger,
            "challenged": challenged,
        }
        expected = {**data, 'game_name': DEFAULT_GAME}
        with patch('server.router.make_challenge') as mock_make_challenge:
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post(
                    "/challenge",
                    json=data
                )
        mock_make_challenge.assert_awaited_once_with(challenger, challenged, DEFAULT_GAME)
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.json(), expected)

    async def test_challenge_error(self):
        data = {
            "challenger": 'challenger',
            "challenged": ['challenged'],
        }
        with patch('server.router.make_challenge') as mock_make_challenge:
            mock_make_challenge.side_effect = Exception()
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post(
                    "/challenge",
                    json=data
                )
        self.assertEqual(response.status_code, 500)

    async def test_update_users_in_django(self):
        user_list = {"users": ["User 1"]}
        user_dict = {'User 1': 'websockets'}

        manager.connections = user_dict

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/users")

        assert response.status_code == 200
        assert response.json() == user_list

    @parameterized.expand([
        (
            'test-0000-0001',
            'token-00000001',
            [
                '00000001',
                ([
                    {'player': 'P1', 'from_row': 3, 'to_row': 2},
                    {'player': 'P2', 'from_row': 1, 'to_row': 3},
                    {'player': 'P1', 'from_row': 2, 'to_row': 1},
                    {'player': 'P2', 'from_row': 3, 'to_row': 4},
                ], 'token-00000002'),
            ],
            200,
        ),
        (
            'test-0000-0002',
            '',
            [
                ([
                    {'player': 'P1', 'from_row': 3, 'to_row': 2},
                    {'player': 'P2', 'from_row': 1, 'to_row': 3},
                    {'player': 'P1', 'from_row': 2, 'to_row': 1},
                    {'player': 'P2', 'from_row': 3, 'to_row': 4},
                ], 'token-00000001'),
            ],
            200,
        ),
        (
            'test-0000-0003',
            None,
            [
                ([
                    {'player': 'P1', 'from_row': 3, 'to_row': 2},
                    {'player': 'P2', 'from_row': 1, 'to_row': 3},
                    {'player': 'P1', 'from_row': 2, 'to_row': 1},
                    {'player': 'P2', 'from_row': 3, 'to_row': 4},
                ], 'token-00000001'),
            ],
            200,
        ),
        (
            '',
            None,
            None,
            400,
        ),
        (
            '',
            'token-00000001',
            None,
            400,
        ),
        (
            'test-0000-0006',
            None,
            ValueError,
            500,
        )
    ])
    async def test_get_match_details(self, test_game_id, test_token, redis_get_return, expected_status):
        with patch('server.router.redis_get') as redis_get_patched:
            async with AsyncClient(app=app, base_url='http://test') as ac:
                redis_get_patched.side_effect = redis_get_return
                response = await ac.get(
                    '/match_details',
                    params={
                        'game_id': test_game_id,
                        'page_token': test_token,
                    },
                )
                self.assertEqual(response.status_code, expected_status)

    async def test_tournament(self):
        players = [['Player 1', 'Player 2'], ['Player 3', 'Player1']]
        tournament_id = 'test_tournament_id'
        data = {
            'tournament_id': tournament_id,
            'players': players,
        }
        expected = {**data, 'game_name': DEFAULT_GAME}
        status = 200
        with patch('server.router.make_tournament') as mock_make_tournament:
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post(
                    "/tournament",
                    json=data,
                )
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.json(), json.dumps(expected))
        mock_make_tournament.assert_awaited_once_with(tournament_id, players, DEFAULT_GAME)

    async def test_tournament_error(self):
        players = [['Player 1', 'Player 2'], ['Player 3', 'Player1']]
        tournament_id = 'test_tournament_id'
        data = {
            'tournament_id': tournament_id,
            'players': players,
        }
        status = 500
        with patch('server.router.make_tournament') as mock_make_tournament:
            mock_make_tournament.side_effect = Exception('test')
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post(
                    "/tournament",
                    json=data,
                )
        self.assertEqual(response.status_code, status)
        mock_make_tournament.assert_awaited_once_with(tournament_id, players, DEFAULT_GAME)
