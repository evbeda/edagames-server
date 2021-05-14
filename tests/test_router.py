import unittest
from unittest.mock import patch
from parameterized import parameterized
from httpx import AsyncClient

from server.server import app, manager

from server.constants import TIME_CHALLENGE


class TestRouter(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        ({"challenger": "Ana", "challenged": "Pepe", "challenge_id": "2138123721"}, 200),
    ])
    async def test_challenge(self, data, status):
        challenge_id = '810a84e7'
        to_json = '''{ players: [player_1, player_2]}'''
        with patch('uuid.uuid4', return_value=challenge_id):
            with patch('server.router.notify_challenge_to_client') as mock_notify_challenge:
                with patch('server.router.save_string') as mock_save:
                    with patch('server.router.data_challenge', return_value=to_json) as mock_data:
                        async with AsyncClient(app=app, base_url="http://test") as ac:
                            response = await ac.post(
                                "/challenge",
                                json=data
                            )
        mock_data.assert_called_once_with(['Ana', 'Pepe'])
        mock_save.assert_called_once_with(
            'c_' + challenge_id,
            to_json,
            TIME_CHALLENGE,
        )
        mock_notify_challenge.assert_awaited_once_with('Pepe', 'Ana', challenge_id)
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.json(), data)

    async def test_update_users_in_django(self):
        user_list = {"users": ["User 1"]}
        user_dict = {'User 1': 'websockets'}

        manager.connections = user_dict

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/users")

        assert response.status_code == 200
        assert response.json() == user_list
