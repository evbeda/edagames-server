import unittest
from unittest.mock import patch
from parameterized import parameterized
from httpx import AsyncClient

from server.server import app, manager


class TestRouter(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        ({"challenger": "Ana", "challenged": "Pepe", "challenge_id": "2138123721"}, 200),
    ])
    async def test_challenge(self, data, status):
        with patch('uuid.uuid4', return_value='810a84e7'):
            with patch('server.router.notify_challenge_to_client') as mock_notify_challenge:
                async with AsyncClient(app=app, base_url="http://test") as ac:
                    response = await ac.post(
                        "/challenge",
                        json=data
                    )
                mock_notify_challenge.assert_awaited_once_with(
                    'Pepe',
                    'Ana',
                    '810a84e7',
                )
        assert response.status_code == status
        assert response.json() == data

    async def test_update_users_in_django(self):
        user_list = {"users": ["User 1"]}
        user_dict = {'User 1': 'websockets'}

        manager.connections = user_dict

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/users")

        assert response.status_code == 200
        assert response.json() == user_list
